"""Pure dataframe transformations with explicit input contracts."""

import numpy as np
import pandas as pd

from .config import DAYS_PER_WEEK


def require_columns(data: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = columns - set(data.columns)
    if missing:
        raise ValueError(f"{label} is missing required columns: {sorted(missing)}")


def numeric_column(data: pd.DataFrame, column: str, *, nullable: bool = False,
                   integer: bool = False) -> pd.Series:
    """Reject malformed values rather than silently converting them to missing."""
    raw = data[column]
    values = pd.to_numeric(raw, errors="coerce")
    invalid = (raw.notna() & values.isna()) | (values.notna() & ~np.isfinite(values))
    if not nullable:
        invalid |= values.isna()
    if integer:
        invalid |= values.notna() & values.mod(1).ne(0)
    if invalid.any():
        raise ValueError(f"Invalid {column}: {int(invalid.sum())} rows")
    return values.astype("Int64") if integer else values


def prepare_airbnb(data: pd.DataFrame) -> pd.DataFrame:
    """Retain upstream cleaning and verify the listing and snapshot grain."""
    require_columns(data, {"id", "price", "longitude", "latitude", "snapshot_date"}, "Airbnb")
    if data.empty:
        raise ValueError("Airbnb input is empty")
    result = data.copy()
    reserved = {"area_code", "area_name", "query_status", "bond_time", "bond_row_matched",
                "active_bonds", "total_bonds", "median_weekly_rent",
                "median_long_term_nightly_rent", "nightly_price_gap"}
    if reserved & set(result.columns):
        raise ValueError("Airbnb input must be the upstream cleaned file, without enrichment columns")
    result["id"] = numeric_column(result, "id", integer=True)
    result["price"] = numeric_column(result, "price", nullable=True)
    for column in ("longitude", "latitude"):
        result[column] = numeric_column(result, column)
    if result["id"].le(0).any() or result["price"].lt(0).any():
        raise ValueError("Listing IDs must be positive and observed prices nonnegative")
    if not result["longitude"].between(166, 179).all() or not result["latitude"].between(-48, -34).all():
        raise ValueError("Coordinates must be within the upstream New Zealand bounds")
    dates = pd.to_datetime(result["snapshot_date"], errors="coerce", format="%Y-%m-%d")
    if dates.isna().any():
        raise ValueError("snapshot_date must contain valid YYYY-MM-DD dates")
    result["snapshot_date"] = dates
    if result.duplicated(["snapshot_date", "id"]).any():
        raise ValueError("Duplicate listing ID within a snapshot")
    if "neighbourhood_group" in result and not result["neighbourhood_group"].eq("Christchurch City").all():
        raise ValueError("Airbnb input contains rows outside Christchurch City")
    result["bond_time"] = dates.dt.to_period("Q").dt.start_time
    # Multiple snapshots in one quarter would weight repeatedly observed listings.
    if result.groupby("bond_time")["snapshot_date"].nunique().gt(1).any():
        raise ValueError("Choose one Airbnb snapshot per quarter before comparison")
    return result


def prepare_bonds(data: pd.DataFrame) -> pd.DataFrame:
    """Select published ALL/ALL totals; never sum overlapping breakdowns."""
    require_columns(data, {"TimeFrame", "Location Id", "Dwelling Type", "Number Of Beds",
                           "Active Bonds", "Total Bonds", "Median Rent"}, "Bond")
    totals = data.loc[data["Dwelling Type"].eq("ALL") & data["Number Of Beds"].eq("ALL")].copy()
    if totals.empty:
        raise ValueError("No ALL/ALL bond totals are available")
    totals["Location Id"] = numeric_column(totals, "Location Id", integer=True)
    if totals["Location Id"].le(0).any():
        raise ValueError("Bond location IDs must be positive; use the Deliverable 4 cleaned input")
    dates = pd.to_datetime(totals["TimeFrame"], errors="coerce", format="%Y-%m-%d")
    if dates.isna().any() or not dates.eq(dates.dt.to_period("Q").dt.start_time).all():
        raise ValueError("Bond TimeFrame must be a calendar-quarter start")
    totals["TimeFrame"] = dates
    for column in ("Median Rent", "Active Bonds", "Total Bonds"):
        totals[column] = numeric_column(totals, column, nullable=True,
                                        integer=column != "Median Rent")
        if totals[column].lt(0).any():
            raise ValueError(f"Negative bond metric: {column}")
    if totals.duplicated(["TimeFrame", "Location Id"]).any():
        raise ValueError("Bond totals must be unique by quarter and Location Id")
    return totals


def join_bonds(enriched: pd.DataFrame, bonds: pd.DataFrame) -> pd.DataFrame:
    """Preserve every listing with a validated many-to-one location-quarter join."""
    right = bonds[["Location Id", "TimeFrame", "Active Bonds", "Total Bonds", "Median Rent"]].rename(
        columns={"Location Id": "area_code", "TimeFrame": "bond_time", "Active Bonds": "active_bonds",
                 "Total Bonds": "total_bonds", "Median Rent": "median_weekly_rent"})
    joined = enriched.merge(right, on=["area_code", "bond_time"], how="left",
                            validate="many_to_one", indicator="_bond_merge", sort=False)
    joined["bond_row_matched"] = joined.pop("_bond_merge").eq("both")
    joined["median_long_term_nightly_rent"] = joined["median_weekly_rent"] / DAYS_PER_WEEK
    joined["nightly_price_gap"] = joined["price"] - joined["median_long_term_nightly_rent"]
    return joined


def summarise_locations(joined: pd.DataFrame) -> pd.DataFrame:
    """Summarise each SA2-quarter separately, including denominators for gaps."""
    summary = joined.groupby(["bond_time", "area_code", "area_name"], dropna=False).agg(
        airbnb_count=("id", "nunique"),
        priced_listing_count=("price", "count"),
        gap_listing_count=("nightly_price_gap", "count"),
        median_airbnb_price=("price", "median"),
        active_bonds=("active_bonds", "first"),
        median_weekly_rent=("median_weekly_rent", "first"),
        median_long_term_nightly_rent=("median_long_term_nightly_rent", "first"),
        median_nightly_gap=("nightly_price_gap", "median"),
    ).reset_index()
    summary["airbnb_minus_active_bonds"] = summary["airbnb_count"] - summary["active_bonds"]
    return summary.sort_values(["bond_time", "area_code"], kind="stable").reset_index(drop=True)


def rank_gaps(summary: pd.DataFrame, minimum: int) -> pd.DataFrame:
    """Rank up to 20 locations per quarter with enough observed price gaps."""
    eligible = summary.loc[summary["gap_listing_count"].ge(minimum) & summary["median_nightly_gap"].notna()]
    return eligible.sort_values(["bond_time", "median_nightly_gap", "area_code"],
                                 ascending=[True, False, True], kind="stable").groupby(
                                     "bond_time", group_keys=False).head(20).reset_index(drop=True)
