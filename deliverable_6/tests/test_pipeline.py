"""Small adversarial examples for the join, cache, and price-gap rules."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from pipeline.geography import enrich_coordinates, load_cache, query_sa2
from pipeline.transforms import join_bonds, prepare_airbnb, prepare_bonds, rank_gaps, summarise_locations
from pipeline.validation import sanity_check


def listings() -> pd.DataFrame:
    return pd.DataFrame(dict(id=[1, 2], price=[100.0, np.nan],
                             longitude=[172.6, 172.7], latitude=[-43.5, -43.6],
                             snapshot_date=["2026-06-19"] * 2))


def bonds() -> pd.DataFrame:
    return pd.DataFrame({"Location Id": [326600, 326600],
                         "TimeFrame": ["2026-04-01"] * 2,
                         "Dwelling Type": ["ALL", "House"], "Number Of Beds": ["ALL", "ALL"],
                         "Median Rent": [560, 999], "Active Bonds": [12, 100], "Total Bonds": [6, 50]})


def enriched() -> pd.DataFrame:
    frame = prepare_airbnb(listings())
    frame["area_code"] = pd.Series([326600, 999999], dtype="Int64")
    frame["area_name"] = ["Central", "Unmatched"]
    return frame


class TransformationTests(unittest.TestCase):
    def test_join_and_independent_hand_calculation(self):
        prepared = prepare_airbnb(listings())
        joined = join_bonds(enriched(), prepare_bonds(bonds()))
        self.assertEqual(len(joined), 2)
        self.assertAlmostEqual(joined.loc[0, "median_long_term_nightly_rent"], 80)
        self.assertAlmostEqual(joined.loc[0, "nightly_price_gap"], 20)
        self.assertFalse(joined.loc[1, "bond_row_matched"])
        self.assertTrue(pd.isna(joined.loc[1, "active_bonds"]))
        evidence = sanity_check(prepared, joined, summarise_locations(joined))
        self.assertTrue(all(evidence["checks"].values()))

    def test_breakdowns_are_not_summed(self):
        totals = prepare_bonds(bonds())
        self.assertEqual(len(totals), 1)
        self.assertEqual(totals.iloc[0]["Active Bonds"], 12)

    def test_duplicate_bond_keys_fail(self):
        total = bonds().iloc[[0]]
        with self.assertRaisesRegex(ValueError, "unique"):
            prepare_bonds(pd.concat([total, total]))

    def test_duplicate_listing_keys_fail(self):
        frame = listings()
        frame.loc[1, "id"] = 1
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            prepare_airbnb(frame)

    def test_invalid_dates_fail(self):
        frame = listings()
        frame.loc[0, "snapshot_date"] = "bad-date"
        with self.assertRaisesRegex(ValueError, "snapshot_date"):
            prepare_airbnb(frame)

    def test_invalid_numeric_price_fails(self):
        frame = listings().astype({"price": "object"})
        frame.loc[0, "price"] = "unparsed currency"
        with self.assertRaisesRegex(ValueError, "price"):
            prepare_airbnb(frame)

    def test_missing_price_is_preserved(self):
        self.assertTrue(pd.isna(prepare_airbnb(listings()).loc[1, "price"]))

    def test_multiple_snapshots_within_quarter_fail(self):
        frame = listings()
        frame.loc[1, "snapshot_date"] = "2026-05-19"
        with self.assertRaisesRegex(ValueError, "one Airbnb snapshot"):
            prepare_airbnb(frame)

    def test_quarters_remain_separate(self):
        frame = pd.concat([enriched().iloc[[0]], enriched().iloc[[0]]], ignore_index=True)
        frame.loc[1, "snapshot_date"] = pd.Timestamp("2026-09-19")
        frame.loc[1, "bond_time"] = pd.Timestamp("2026-07-01")
        totals = pd.concat([prepare_bonds(bonds()), prepare_bonds(bonds())], ignore_index=True)
        totals.loc[1, "TimeFrame"] = pd.Timestamp("2026-07-01")
        totals.loc[1, "Median Rent"] = 700
        summary = summarise_locations(join_bonds(frame, totals))
        self.assertEqual(len(summary), 2)
        self.assertEqual(summary["median_nightly_gap"].tolist(), [20, 0])

    def test_minimum_requires_observed_gaps(self):
        frame = pd.concat([enriched().iloc[[0]]] * 5, ignore_index=True)
        frame["id"] = range(1, 6)
        frame.loc[1:, "price"] = np.nan
        summary = summarise_locations(join_bonds(frame, prepare_bonds(bonds())))
        self.assertEqual(summary.iloc[0]["airbnb_count"], 5)
        self.assertEqual(summary.iloc[0]["gap_listing_count"], 1)
        self.assertTrue(rank_gaps(summary, 5).empty)

    def test_matched_row_with_missing_rent_is_distinct(self):
        total = prepare_bonds(bonds())
        total.loc[0, "Median Rent"] = np.nan
        joined = join_bonds(enriched(), total)
        self.assertTrue(joined.loc[0, "bond_row_matched"])
        self.assertTrue(pd.isna(joined.loc[0, "nightly_price_gap"]))

    def test_arithmetic_corruption_is_detected(self):
        joined = join_bonds(enriched(), prepare_bonds(bonds()))
        joined.loc[0, "nightly_price_gap"] = 999
        with self.assertRaisesRegex(ValueError, "nightly_gap_arithmetic"):
            sanity_check(prepare_airbnb(listings()), joined, summarise_locations(joined))

    def test_expanded_join_is_detected(self):
        joined = join_bonds(enriched(), prepare_bonds(bonds()))
        broken = pd.concat([joined, joined.iloc[[0]]])
        with self.assertRaisesRegex(ValueError, "row_count"):
            sanity_check(prepare_airbnb(listings()), broken, summarise_locations(broken))

    def test_invalid_quarter_start_fails(self):
        frame = bonds()
        frame.loc[0, "TimeFrame"] = "2026-06-01"
        with self.assertRaisesRegex(ValueError, "quarter"):
            prepare_bonds(frame)


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "cache.csv"
        self.cache = pd.DataFrame(dict(longitude=[172.6, 172.7], latitude=[-43.5, -43.6],
                                       area_code=[326600, 999999], area_name=["Central", "Other"],
                                       query_status=["ok", "ok"]))

    def test_complete_cache_needs_no_api_key_or_query(self):
        self.cache.to_csv(self.path, index=False)
        with patch("pipeline.geography.query_sa2", side_effect=AssertionError("Network called")), patch.dict("os.environ", {}, clear=True):
            result = enrich_coordinates(prepare_airbnb(listings()), load_cache(self.path), False, 1,
                                         Path(self.temp.name) / "new.csv")
        self.assertEqual(len(result), 2)

    def test_failed_cache_is_not_treated_as_completed(self):
        self.cache.loc[0, ["area_code", "area_name"]] = [np.nan, None]
        self.cache.loc[0, "query_status"] = "network_error"
        self.cache.to_csv(self.path, index=False)
        with self.assertRaisesRegex(ValueError, "missing or failed"):
            enrich_coordinates(prepare_airbnb(listings()), load_cache(self.path), False, 1,
                                 Path(self.temp.name) / "new.csv")

    def test_duplicate_cache_keys_fail(self):
        pd.concat([self.cache, self.cache.iloc[[0]]]).to_csv(self.path, index=False)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            load_cache(self.path)

    def test_timeout_is_safe_and_does_not_access_reason_attribute(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("contains secret-url")):
            result = query_sa2(172.6, -43.5, "dummy-key", retries=1)
        self.assertEqual(result["query_status"], "network_error")
        self.assertNotIn("secret", str(result))

    def test_failed_cache_retries_in_live_mode(self):
        self.cache.loc[0, ["area_code", "area_name"]] = [np.nan, None]
        self.cache.loc[0, "query_status"] = "network_error"
        self.cache.to_csv(self.path, index=False)
        with patch("pipeline.geography.query_sa2", return_value=dict(area_code=326600, area_name="Central", query_status="ok")) as query, patch.dict("os.environ", {"KOORDINATES_API_KEY": "dummy"}):
            result = enrich_coordinates(prepare_airbnb(listings()), load_cache(self.path), True, 1,
                                         Path(self.temp.name) / "new.csv")
        self.assertEqual(query.call_count, 1)
        self.assertTrue(result["query_status"].eq("ok").all())


if __name__ == "__main__":
    unittest.main()
