"""Deterministic cleaning, exact quarterly joins, and explicit denominators."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def require_columns(frame, columns, label):
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f"{label} is missing columns: {sorted(missing)}")


def number(series):
    return pd.to_numeric(series.astype("string").str.replace(r"[$,]", "", regex=True), errors="coerce").astype("float64")


def clean_airbnb(root: Path, manifest: dict, config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    cleaned, audit = [], []
    for source in manifest["airbnb"]:
        raw = pd.read_csv(root / source["path"], dtype="string", keep_default_na=True)
        require_columns(raw, ["id", "neighbourhood_group", "longitude", "latitude", "price", "room_type",
                              "minimum_nights", "availability_365"], source["path"])
        frame = raw.loc[raw.neighbourhood_group.str.strip().eq(config["city"])].copy()
        n_city = len(frame)
        frame["source_row"] = frame.index + 2
        # Source-row lineage must not prevent exact duplicate detection.
        duplicates = frame.drop(columns="source_row").duplicated()
        frame = frame.loc[~duplicates].copy()
        if frame.id.duplicated().any():
            raise ValueError(f"Conflicting repeated listing IDs in {source['snapshot_month']}")
        frame["snapshot_date"] = pd.Timestamp(source["snapshot_date"])
        frame["snapshot_month"] = source["snapshot_month"]
        frame["quarter_start"] = frame.snapshot_date.dt.to_period("Q").dt.start_time
        frame["source_file"] = source["path"]
        frame["price_raw"] = frame.price
        for col in ["longitude", "latitude", "price", "minimum_nights", "availability_365", "number_of_reviews",
                    "number_of_reviews_ltm", "reviews_per_month", "calculated_host_listings_count"]:
            if col in frame:
                frame[col] = number(frame[col])
        valid_key = frame.id.str.fullmatch(r"\d+", na=False)
        valid_xy = frame.longitude.between(-180, 180) & frame.latitude.between(-90, 90)
        # City membership comes from the publisher's city label and is independently
        # checked by the official city polygons during enrichment.
        excluded = frame.loc[~(valid_key & valid_xy)].copy()
        if not excluded.empty:
            folder = root / "outputs/tables"
            folder.mkdir(parents=True, exist_ok=True)
            excluded.to_csv(folder / f"excluded_airbnb_{source['snapshot_month']}.csv", index=False)
        frame = frame.loc[valid_key & valid_xy].copy()
        invalid_price = frame.price.notna() & frame.price.le(0)
        frame.loc[invalid_price, "price"] = np.nan
        frame["price_missing_or_invalid"] = frame.price.isna()
        frame["availability_invalid"] = ~frame.availability_365.between(0, 365)
        frame.loc[frame.availability_invalid, "availability_365"] = np.nan
        frame["minimum_nights_invalid"] = frame.minimum_nights.isna() | frame.minimum_nights.lt(1)
        frame.loc[frame.minimum_nights_invalid, "minimum_nights"] = np.nan
        frame["last_review"] = pd.to_datetime(frame.last_review, errors="coerce")
        frame["days_since_last_review"] = (frame.snapshot_date - frame.last_review).dt.days
        frame["review_after_snapshot"] = frame.days_since_last_review.lt(0)
        frame["entire_short_stay"] = frame.room_type.eq("Entire home/apt") & frame.minimum_nights.le(
            config["maximum_short_stay_minimum_nights"])
        frame["entire_short_stay_with_availability"] = frame.entire_short_stay & frame.availability_365.gt(0)
        # Flag rather than trim high prices; there is no justified universal cap.
        threshold = frame.groupby("room_type", observed=True).price.transform(lambda x: x.quantile(.99))
        frame["high_price_flag"] = frame.price.gt(threshold)
        audit.append({"snapshot_month": source["snapshot_month"], "source_rows": len(raw),
                      "city_rows_before_cleaning": n_city, "exact_duplicates_removed": int(duplicates.sum()),
                      "invalid_key_or_coordinates_removed": len(excluded), "retained_rows": len(frame),
                      "missing_or_invalid_prices_retained": int(frame.price.isna().sum()),
                      "nonpositive_prices_set_missing": int(invalid_price.sum()),
                      "availability_invalid": int(frame.availability_invalid.sum()),
                      "review_after_snapshot": int(frame.review_after_snapshot.sum()),
                      "high_prices_flagged_retained": int(frame.high_price_flag.sum())})
        cleaned.append(frame)
    result = pd.concat(cleaned, ignore_index=True)
    if result.duplicated(["id", "snapshot_month"]).any():
        raise ValueError("Listing-month key is not unique")
    result = result.rename(columns={"id": "listing_id", "price": "airbnb_nightly_nzd"})
    return result, pd.DataFrame(audit)


def clean_bonds(root: Path, manifest: dict, areas, config: dict):
    raw = pd.read_csv(root / manifest["bonds"]["path"], dtype="string", na_values=["NULL"])
    require_columns(raw, ["TimeFrame", "Location Id", "Dwelling Type", "Number Of Beds", "Median Rent",
                          "Total Bonds", "Active Bonds", "Closed Bonds"], "Bond data")
    raw["source_row"] = raw.index + 2
    raw["quarter_start"] = pd.to_datetime(raw.TimeFrame, errors="coerce")
    start = pd.Period(config["start_month"], freq="M").asfreq("Q").start_time
    end = pd.Period(config["end_month"], freq="M").asfreq("Q").start_time
    selected = raw.loc[raw.quarter_start.between(start, end)].copy()
    selected["area_code"] = selected["Location Id"].str.strip()
    valid = selected.area_code.str.fullmatch(r"\d{6}", na=False)
    valid_selected = selected.loc[valid].copy()
    city = valid_selected.loc[valid_selected.area_code.isin(areas.area_code)].copy()
    mapping = {"Dwelling Type": "dwelling_type", "Number Of Beds": "number_of_beds",
               "Total Bonds": "bonds_lodged", "Active Bonds": "active_bonds", "Closed Bonds": "closed_bonds",
               "Median Rent": "bond_weekly_median_nzd", "Geometric Mean Rent": "bond_weekly_geomean_nzd",
               "Lower Quartile Rent": "bond_weekly_lower_quartile_nzd",
               "Upper Quartile Rent": "bond_weekly_upper_quartile_nzd"}
    mapping["Log Std Dev Weekly Rent"] = "bond_log_std_weekly_rent"
    city = city.rename(columns=mapping)
    keys = ["area_code", "quarter_start", "dwelling_type", "number_of_beds"]
    duplicates = city.drop(columns="source_row").duplicated()
    city = city.loc[~duplicates].copy()
    if city.duplicated(keys).any():
        raise ValueError("Conflicting duplicate bond keys; refusing a many-to-many join")
    for col in [v for v in mapping.values() if v not in ("dwelling_type", "number_of_beds")]:
        if col in city:
            city[col] = number(city[col])
            if col.startswith("bond_weekly"):
                city.loc[city[col].le(0), col] = np.nan
            elif city[col].dropna().lt(0).any():
                raise ValueError(f"Negative bond count in {col}")
    city = city.merge(areas[["area_code", "area_name"]], on="area_code", how="left", validate="many_to_one")
    main = city.loc[city.dwelling_type.eq("ALL") & city.number_of_beds.eq("ALL")].copy()
    main["bond_nightly_equivalent_nzd"] = main.bond_weekly_median_nzd / 7
    if main.duplicated(["area_code", "quarter_start"]).any():
        raise ValueError("ALL/ALL bond rows are not unique by area and quarter")
    audit = {"source_rows": len(raw), "rows_in_requested_quarters": len(selected),
             "invalid_or_missing_area_codes_excluded": int((~valid).sum()),
             "city_detailed_rows": len(city), "city_all_all_rows": len(main),
             "exact_duplicates_removed": int(duplicates.sum()),
             "available_quarters": sorted(main.quarter_start.dt.strftime("%Y-%m-%d").unique().tolist()),
             "missing_main_rents": int(main.bond_weekly_median_nzd.isna().sum())}
    return city, main, audit


def merge_sources(airbnb, bonds):
    columns = ["area_code", "quarter_start", "bond_weekly_median_nzd", "bond_nightly_equivalent_nzd",
               "bonds_lodged", "active_bonds", "closed_bonds"]
    joined = airbnb.merge(bonds[columns], on=["area_code", "quarter_start"], how="left",
                           validate="many_to_one", indicator="bond_join_status")
    if len(joined) != len(airbnb):
        raise ValueError("The bond join changed the Airbnb row count")
    joined["bond_row_matched"] = joined.bond_join_status.eq("both")
    joined["nightly_price_gap_nzd"] = joined.airbnb_nightly_nzd - joined.bond_nightly_equivalent_nzd
    joined["airbnb_to_bond_ratio"] = joined.airbnb_nightly_nzd / joined.bond_nightly_equivalent_nzd
    joined["comparison_status"] = np.select(
        [joined.area_code.isna(), ~joined.bond_row_matched, joined.bond_weekly_median_nzd.isna(),
         joined.airbnb_nightly_nzd.isna()],
        ["unassigned_location", "no_bond_row_for_quarter", "bond_rent_suppressed_or_missing", "airbnb_price_missing"],
        default="price_comparison_available")
    return joined


def summarise(joined, bonds, areas, config):
    """Keep a full city-area/month grid, including areas without listings."""
    months = [str(x) for x in pd.period_range(config["start_month"], config["end_month"], freq="M")]
    segments = {"all_rooms": pd.Series(True, index=joined.index),
                "entire_short_stay": joined.entire_short_stay,
                "entire_short_stay_with_availability": joined.entire_short_stay_with_availability,
                "entire_short_stay_away_from_boundary": joined.entire_short_stay &
                    ~joined.near_sa2_boundary & joined.area_code.notna()}
    rows, city_rows = [], []
    for segment, mask in segments.items():
        selected = joined.loc[mask]
        for month in months:
            f = selected.loc[selected.snapshot_month.eq(month)]
            observed_month = joined.snapshot_month.eq(month).any()
            groups = f.groupby("area_code", observed=True)
            for area in areas.itertuples():
                group = groups.get_group(area.area_code) if area.area_code in groups.groups else f.iloc[:0]
                quarter = pd.Period(month, freq="M").asfreq("Q").start_time
                b = bonds.loc[bonds.area_code.eq(area.area_code) & bonds.quarter_start.eq(quarter)]
                bond = b.iloc[0] if len(b) else None
                n = len(group)
                prices = group.airbnb_nightly_nzd.dropna()
                gaps = group.nightly_price_gap_nzd.dropna()
                eligible = len(gaps) >= config["minimum_priced_listings"]
                rows.append({"snapshot_month": month, "quarter_start": quarter, "segment": segment,
                             "area_code": area.area_code, "area_name": area.area_name,
                             "airbnb_listing_count": n if observed_month else np.nan,
                             "airbnb_priced_count": len(prices) if observed_month else np.nan,
                             "usable_gap_count": len(gaps) if observed_month else np.nan,
                             "airbnb_median_nightly_nzd": prices.median() if len(prices) else np.nan,
                             "airbnb_p25_nightly_nzd": prices.quantile(.25) if len(prices) else np.nan,
                             "airbnb_p75_nightly_nzd": prices.quantile(.75) if len(prices) else np.nan,
                             "bond_weekly_median_nzd": bond.bond_weekly_median_nzd if bond is not None else np.nan,
                             "bond_nightly_equivalent_nzd": bond.bond_nightly_equivalent_nzd if bond is not None else np.nan,
                             "median_nightly_gap_nzd": gaps.median() if len(gaps) else np.nan,
                             "median_price_ratio": group.airbnb_to_bond_ratio.median() if len(gaps) else np.nan,
                             "bond_row_available": bond is not None,
                             "active_bonds": bond.active_bonds if bond is not None else np.nan,
                             "bonds_lodged": bond.bonds_lodged if bond is not None else np.nan,
                             "airbnb_listings_per_active_bond": n / bond.active_bonds
                                 if observed_month and bond is not None and pd.notna(bond.active_bonds) and bond.active_bonds > 0 else np.nan,
                             "eligible_gap_ranking": eligible,
                             "priced_count_meets_threshold": len(prices) >= config["minimum_priced_listings"],
                             "snapshot_available": bool(observed_month)})
            city_rows.append({"snapshot_month": month, "segment": segment,
                              "listing_count": len(f) if observed_month else np.nan,
                              "priced_count": int(f.airbnb_nightly_nzd.notna().sum()) if observed_month else np.nan,
                              "airbnb_median_nightly_nzd": f.airbnb_nightly_nzd.median(),
                              "matched_listing_count": int(f.bond_row_matched.sum()) if observed_month else np.nan,
                              "usable_gap_count": int(f.nightly_price_gap_nzd.notna().sum()) if observed_month else np.nan,
                              "median_listing_gap_nzd": f.nightly_price_gap_nzd.median(),
                              "listing_weighted_area_bond_nightly_median_nzd": f.bond_nightly_equivalent_nzd.median(),
                              "geographic_assignment_rate": f.area_code.notna().mean(),
                              "bond_row_match_rate": f.bond_row_matched.mean(),
                              "airbnb_price_missing_rate": f.airbnb_nightly_nzd.isna().mean(),
                              "snapshot_available": bool(observed_month)})
    return pd.DataFrame(rows), pd.DataFrame(city_rows)
