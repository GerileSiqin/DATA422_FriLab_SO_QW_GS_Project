"""Executable sanity checks on join grain, units, coverage, and summaries."""

import numpy as np
import pandas as pd


def sanity_check(airbnb: pd.DataFrame, joined: pd.DataFrame,
                 summary: pd.DataFrame) -> dict:
    """Raise on inconsistent output; return measured evidence for the tutor."""
    checks = {}

    def check(name: str, passed: bool) -> None:
        checks[name] = bool(passed)
        if not passed:
            raise ValueError(f"Sanity check failed: {name}")

    check("left_join_preserves_row_count", len(airbnb) == len(joined))
    original_keys = sorted(zip(airbnb["id"], airbnb["snapshot_date"]))
    joined_keys = sorted(zip(joined["id"], joined["snapshot_date"]))
    check("left_join_preserves_listing_snapshot_keys", original_keys == joined_keys)
    check("no_duplicate_listing_snapshot_keys", not joined.duplicated(["id", "snapshot_date"]).any())
    check("summary_counts_reconcile", int(summary["airbnb_count"].sum()) == len(airbnb))
    check("summary_gap_counts_reconcile", int(summary["gap_listing_count"].sum()) == int(joined["nightly_price_gap"].notna().sum()))
    check("snapshot_maps_to_containing_quarter", joined["bond_time"].eq(joined["snapshot_date"].dt.to_period("Q").dt.start_time).all())
    check("weekly_to_nightly_units", np.allclose(joined["median_long_term_nightly_rent"].astype(float),
                                                  joined["median_weekly_rent"].astype(float) / 7.0,
                                                  equal_nan=True))
    check("nightly_gap_arithmetic", np.allclose(joined["nightly_price_gap"].astype(float),
                                                 joined["price"].astype(float) - joined["median_weekly_rent"].astype(float) / 7.0,
                                                 equal_nan=True))
    unmatched = ~joined["bond_row_matched"]
    check("unmatched_bonds_remain_missing", joined.loc[unmatched, ["active_bonds", "median_weekly_rent", "nightly_price_gap"]].isna().all().all())
    return dict(checks=checks, airbnb_rows=len(airbnb), joined_rows=len(joined),
                priced_listings=int(airbnb["price"].notna().sum()),
                missing_prices=int(airbnb["price"].isna().sum()),
                sa2_matches=int(joined["area_code"].notna().sum()),
                bond_row_matches=int(joined["bond_row_matched"].sum()),
                bond_rent_matches=int(joined["median_weekly_rent"].notna().sum()),
                usable_price_gaps=int(joined["nightly_price_gap"].notna().sum()),
                location_quarter_groups=len(summary))
