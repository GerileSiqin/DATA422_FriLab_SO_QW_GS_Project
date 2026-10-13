"""Enrich Airbnb points with SA2 codes, join bond data, analyse, plot, and save SQLite.

The Koordinates API key is read only from KOORDINATES_API_KEY. Results are cached
by coordinate so an interrupted run resumes without repeating completed queries.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ENDPOINT = "https://koordinates.com/services/query/v1/vector.json"
LAYER_ID = 123515
CODE_FIELD = "SA22026_V1_00"
NAME_FIELD = "SA22026_V1_00_NAME"


def query_sa2(longitude: float, latitude: float, api_key: str, retries: int = 5) -> dict:
    parameters = {
        "key": api_key,
        "layer": LAYER_ID,
        "x": longitude,
        "y": latitude,
        "max_results": 1,
        "radius": 1,
        "geometry": "false",
        "with_field_names": "true",
    }
    url = ENDPOINT + "?" + urllib.parse.urlencode(parameters)
    request = urllib.request.Request(url, headers={"User-Agent": "DATA422-Airbnb-SA2/1.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = json.load(response)
            features = payload["vectorQuery"]["layers"][str(LAYER_ID)]["features"]
            if not features:
                return {"area_code": None, "area_name": None, "query_status": "no_match"}
            props = features[0]["properties"]
            return {
                "area_code": props.get(CODE_FIELD),
                "area_name": props.get(NAME_FIELD),
                "query_status": "ok",
            }
        except urllib.error.HTTPError as error:
            if error.code in {429, 500, 502, 503, 504} and attempt < retries - 1:
                time.sleep(2**attempt)
                continue
            body = error.read().decode(errors="replace")[:200]
            return {"area_code": None, "area_name": None, "query_status": f"http_{error.code}: {body}"}
        except (TimeoutError, urllib.error.URLError) as error:
            if attempt < retries - 1:
                time.sleep(2**attempt)
                continue
            return {"area_code": None, "area_name": None, "query_status": f"network_error: {error.reason}"}
    return {"area_code": None, "area_name": None, "query_status": "unknown_error"}


def enrich_coordinates(airbnb: pd.DataFrame, cache_path: Path, api_key: str, workers: int) -> pd.DataFrame:
    coordinates = airbnb[["longitude", "latitude"]].drop_duplicates().copy()
    if cache_path.exists():
        cache = pd.read_csv(cache_path, dtype={"area_code": "string"})
    else:
        cache = pd.DataFrame(columns=["longitude", "latitude", "area_code", "area_name", "query_status"])

    completed = set(zip(cache.get("longitude", []), cache.get("latitude", [])))
    pending = [tuple(row) for row in coordinates.itertuples(index=False, name=None) if tuple(row) not in completed]
    print(f"Unique coordinates: {len(coordinates):,}; cached: {len(completed):,}; pending: {len(pending):,}")

    new_rows: list[dict] = []
    if pending:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(query_sa2, longitude, latitude, api_key): (longitude, latitude)
                for longitude, latitude in pending
            }
            for number, future in enumerate(as_completed(futures), start=1):
                longitude, latitude = futures[future]
                result = future.result()
                new_rows.append({"longitude": longitude, "latitude": latitude, **result})
                if number % 100 == 0 or number == len(pending):
                    updated = pd.concat([cache, pd.DataFrame(new_rows)], ignore_index=True)
                    updated.to_csv(cache_path, index=False)
                    print(f"Saved {number:,}/{len(pending):,} new coordinate results")
        cache = pd.read_csv(cache_path, dtype={"area_code": "string"})

    enriched = airbnb.merge(cache, on=["longitude", "latitude"], how="left", validate="many_to_one")
    enriched["area_code"] = pd.to_numeric(enriched["area_code"], errors="coerce").astype("Int64")
    return enriched


def prepare_bonds(path: Path) -> pd.DataFrame:
    bonds = pd.read_csv(path)
    bonds["TimeFrame"] = pd.to_datetime(bonds["TimeFrame"], errors="coerce")
    bonds["Location Id"] = pd.to_numeric(bonds["Location Id"], errors="coerce").astype("Int64")
    # ALL/ALL is already the published location-level total. Other rows are
    # breakdowns; summing them would double count the same tenancies.
    location_totals = bonds[
        bonds["Dwelling Type"].astype(str).eq("ALL")
        & bonds["Number Of Beds"].astype(str).eq("ALL")
        & bonds["Location Id"].notna()
    ].copy()
    if location_totals.duplicated(["TimeFrame", "Location Id"]).any():
        raise ValueError("Bond location totals are not unique by quarter and Location Id.")
    return location_totals


def save_plot_gap(comparison: pd.DataFrame, path: Path) -> None:
    plot_data = comparison.query("airbnb_count >= 5").nlargest(15, "median_nightly_gap").sort_values("median_nightly_gap")
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(plot_data["area_name"], plot_data["median_nightly_gap"], color="#2563A6")
    ax.axvline(0, color="#333333", linewidth=1)
    ax.set_xlabel("Median gap: Airbnb nightly price − long-term nightly rent (NZD)")
    ax.set_ylabel("Statistical Area 2")
    ax.set_title("Largest short-term vs long-term rental price gaps")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_plot_counts(comparison: pd.DataFrame, path: Path) -> None:
    plot_data = comparison.nlargest(20, "airbnb_count").sort_values("airbnb_count")
    y = list(range(len(plot_data)))
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh([value - 0.2 for value in y], plot_data["active_bonds"], height=0.4, label="Active long-term bonds", color="#D9A441")
    ax.barh([value + 0.2 for value in y], plot_data["airbnb_count"], height=0.4, label="Airbnb listings", color="#2563A6")
    ax.set_yticks(list(y), labels=plot_data["area_name"])
    ax.set_xlabel("Properties/listings (different source definitions)")
    ax.set_title("Airbnb listings and active rental bonds by location")
    ax.legend()
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--airbnb", type=Path, default=here.parent / "deliverable_3/data_processed/christchurch_airbnb_cleaned.csv")
    parser.add_argument("--bonds", type=Path, default=here.parent / "deliverable_4/bond_data_processed/bond_data_clean_qi.csv")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    api_key = os.getenv("KOORDINATES_API_KEY")
    if not api_key:
        raise SystemExit("Set KOORDINATES_API_KEY in the VS Code terminal before running.")
    if not 1 <= args.workers <= 16:
        raise SystemExit("--workers must be between 1 and 16.")

    data_dir = here / "data_processed"
    results_dir = here / "results"
    plots_dir = results_dir / "plots"
    for directory in (data_dir, results_dir, plots_dir):
        directory.mkdir(parents=True, exist_ok=True)

    airbnb = pd.read_csv(args.airbnb)
    required = {"latitude", "longitude", "price", "snapshot_date", "id"}
    missing = required - set(airbnb.columns)
    if missing:
        raise ValueError(f"Airbnb input is missing required columns: {sorted(missing)}")
    airbnb["snapshot_date"] = pd.to_datetime(airbnb["snapshot_date"], errors="coerce")
    airbnb["price"] = pd.to_numeric(airbnb["price"], errors="coerce")

    # Mandatory one-point test before the batch.
    first = airbnb.dropna(subset=["longitude", "latitude"]).iloc[0]
    test = query_sa2(float(first["longitude"]), float(first["latitude"]), api_key)
    if test["query_status"] != "ok":
        raise RuntimeError(f"Single-query test failed: {test['query_status']}")
    print(f"Single-query test passed: {test['area_code']} — {test['area_name']}")

    cache_path = results_dir / "koordinates_coordinate_cache.csv"
    enriched = enrich_coordinates(airbnb, cache_path, api_key, args.workers)
    enriched_path = data_dir / "christchurch_airbnb_with_sa2.csv"
    enriched.to_csv(enriched_path, index=False)

    bonds = prepare_bonds(args.bonds)
    bonds_path = data_dir / "bond_location_quarter_totals.csv"
    bonds.to_csv(bonds_path, index=False, date_format="%Y-%m-%d")

    # Snapshot 2026-06-19 maps to its containing 2026-Q2 bond period (2026-04-01).
    enriched["bond_time"] = enriched["snapshot_date"].dt.to_period("Q").dt.start_time
    enriched["area_code"] = enriched["area_code"].astype("Int64")

    database = here / "deliverable_5.sqlite"
    with sqlite3.connect(database) as connection:
        enriched.to_sql("airbnb_enriched", connection, if_exists="replace", index=False)
        bonds.to_sql("bond_location_quarter", connection, if_exists="replace", index=False)
        sql = """
        SELECT a.*,
               b.[Active Bonds] AS active_bonds,
               b.[Total Bonds] AS total_bonds,
               b.[Median Rent] AS median_weekly_rent,
               b.[Median Rent] / 7.0 AS median_long_term_nightly_rent,
               a.price - b.[Median Rent] / 7.0 AS nightly_price_gap
        FROM airbnb_enriched AS a
        LEFT JOIN bond_location_quarter AS b
          ON CAST(a.area_code AS INTEGER) = CAST(b.[Location Id] AS INTEGER)
         AND date(a.bond_time) = date(b.TimeFrame)
        """
        joined = pd.read_sql_query(sql, connection)
        joined.to_sql("airbnb_bond_joined", connection, if_exists="replace", index=False)

    joined_path = data_dir / "airbnb_bond_joined.csv"
    joined.to_csv(joined_path, index=False)

    comparison = (
        joined.groupby(["area_code", "area_name"], dropna=False)
        .agg(
            airbnb_count=("id", "nunique"),
            median_airbnb_price=("price", "median"),
            active_bonds=("active_bonds", "max"),
            median_weekly_rent=("median_weekly_rent", "max"),
            median_long_term_nightly_rent=("median_long_term_nightly_rent", "max"),
            median_nightly_gap=("nightly_price_gap", "median"),
        )
        .reset_index()
    )
    comparison["airbnb_minus_active_bonds"] = comparison["airbnb_count"] - comparison["active_bonds"]
    comparison.to_csv(results_dir / "location_comparison.csv", index=False)
    comparison.query("airbnb_count >= 5").nlargest(20, "median_nightly_gap").to_csv(
        results_dir / "largest_gap_locations.csv", index=False
    )

    central = enriched.loc[enriched["area_code"].eq(326600), "price"].dropna()
    central_median = float(central.median()) if not central.empty else None
    matched_sa2 = int(enriched["area_code"].notna().sum())
    joined_rent = int(joined["median_weekly_rent"].notna().sum())
    eligible_gaps = comparison.query("airbnb_count >= 5 and median_nightly_gap == median_nightly_gap")
    largest = eligible_gaps.nlargest(1, "median_nightly_gap")
    largest_record = largest.iloc[0].to_dict() if not largest.empty else None

    quality = {
        "airbnb_rows": len(airbnb),
        "unique_listing_ids": int(airbnb["id"].nunique()),
        "duplicate_listing_ids": int(airbnb.duplicated("id").sum()),
        "sa2_matches": matched_sa2,
        "sa2_match_rate": matched_sa2 / len(airbnb),
        "bond_join_matches": joined_rent,
        "bond_join_match_rate": joined_rent / len(joined),
        "price_missing": int(airbnb["price"].isna().sum()),
        "central_listing_count": int(len(central)),
    }
    (results_dir / "data_quality_summary.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")

    save_plot_gap(comparison, plots_dir / "01_largest_price_gaps.png")
    save_plot_counts(comparison, plots_dir / "02_property_counts.png")

    if largest_record:
        gap_text = (
            f"{largest_record['area_name']} (Location ID {int(largest_record['area_code'])}), "
            f"median nightly gap NZ${largest_record['median_nightly_gap']:.2f}, "
            f"based on {int(largest_record['airbnb_count'])} Airbnb listings"
        )
    else:
        gap_text = "Unavailable because no location met the five-listing minimum with a bond match"
    summary = f"""# Deliverable 5 results

## Key answers

- Stats NZ dataset: **Statistical Area 2 2026**, Koordinates layer ID **{LAYER_ID}**.
- Christchurch Central (Location ID 326600) median Airbnb nightly price: **{f'NZ${central_median:.2f}' if central_median is not None else 'not available'}** from **{len(central)}** listings.
- Largest median short-term/long-term nightly price gap (minimum five Airbnb listings): **{gap_text}**.
- SA2 enrichment coverage: **{matched_sa2:,}/{len(airbnb):,} ({matched_sa2 / len(airbnb):.1%})**.
- Bond join coverage: **{joined_rent:,}/{len(joined):,} ({joined_rent / len(joined):.1%})**.

## Method

The Airbnb snapshot date is mapped to the start of its calendar quarter. The June 2026 snapshot therefore joins to the April 2026 bond quarter. A **left join from Airbnb** retains every Airbnb listing while adding the matching location-quarter bond statistics. Only bond rows with `Dwelling Type = ALL` and `Number Of Beds = ALL` are used, preventing double counting across published breakdowns.

Long-term nightly rent is the published median weekly rent divided by seven. Each listing gap is Airbnb nightly price minus that value. The location ranking uses the median listing gap and requires at least five Airbnb listings to reduce unstable small-sample extremes.

`Active Bonds` is used as the closest available proxy for long-term rental property count. The supplied Airbnb file has no beds field, so a beds comparison would not be defensible from these inputs.

## Reproducibility and privacy

The API key is read from `KOORDINATES_API_KEY` and is never written to outputs. Coordinate results are cached in `results/koordinates_coordinate_cache.csv`, so successful calls are not repeated. The SQLite database contains the two prepared tables and the SQL-joined result.
"""
    (results_dir / "analysis_summary.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
