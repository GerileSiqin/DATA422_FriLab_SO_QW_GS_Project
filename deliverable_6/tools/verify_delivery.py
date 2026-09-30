"""Verify saved artifacts, regression against Deliverable 5, and edge tests."""

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from pipeline.outputs import file_hash


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=HERE.parent)
    args = parser.parse_args()
    results = HERE / "results"
    prior = args.project_root / "Deliverable_5"
    manifest = json.loads((results / "run_manifest.json").read_text())
    checks = {}
    for name, entry in manifest["inputs"].items():
        assert file_hash(Path(entry["path"])) == entry["sha256"], name
    checks["inputs_unchanged_after_run"] = True
    for name, digest in manifest["outputs"].items():
        assert file_hash(results / name) == digest, name
    checks["pipeline_output_fingerprints_match"] = True
    old = pd.read_csv(prior / "results/location_comparison.csv")
    new = pd.read_csv(results / "data_processed/location_comparison.csv")
    cols = list(old.columns)
    pd.testing.assert_frame_equal(new[cols].sort_values("area_code").reset_index(drop=True),
                                  old.sort_values("area_code").reset_index(drop=True),
                                  check_dtype=False, rtol=1e-10, atol=1e-10)
    checks["all_174_prior_location_statistics_preserved"] = True
    old_join = pd.read_csv(prior / "data_processed/airbnb_bond_joined.csv")
    new_join = pd.read_csv(results / "data_processed/airbnb_bond_joined.csv")
    for column in ("snapshot_date", "bond_time"):
        old_join[column] = pd.to_datetime(old_join[column])
        new_join[column] = pd.to_datetime(new_join[column])
    pd.testing.assert_frame_equal(new_join[list(old_join.columns)], old_join,
                                  check_dtype=False, rtol=1e-10, atol=1e-10)
    checks["all_prior_joined_values_preserved"] = True
    with sqlite3.connect(results / "deliverable_6.sqlite") as connection:
        names = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", connection)["name"]
        assert len(names) == 6
        for name in names:
            saved = pd.read_csv(results / "data_processed" / f"{name}.csv")
            stored = pd.read_sql_query(f'SELECT * FROM "{name}"', connection)
            assert saved.shape == stored.shape, name
            for column in ("snapshot_date", "bond_time", "TimeFrame", "last_review"):
                if column in saved:
                    saved[column] = pd.to_datetime(saved[column])
                    stored[column] = pd.to_datetime(stored[column])
            if "bond_row_matched" in saved:
                stored["bond_row_matched"] = stored["bond_row_matched"].astype(bool)
            for column in saved.columns:
                if saved[column].isna().all() and stored[column].isna().all():
                    # CSV represents missing values as NaN; SQLite uses NULL.
                    saved[column] = float("nan")
                    stored[column] = float("nan")
            pd.testing.assert_frame_equal(saved, stored, check_dtype=False, rtol=1e-10, atol=1e-10)
    checks["all_six_sqlite_tables_equal_csv_contents"] = True
    ranked = pd.read_csv(results / "data_processed/largest_gap_locations.csv")
    minimum = manifest["settings"]["minimum_priced_listings"]
    assert ranked["gap_listing_count"].ge(minimum).all()
    assert ranked["median_nightly_gap"].notna().all()
    checks["ranking_uses_observed_gap_denominator"] = True
    excluded = new.loc[new["airbnb_count"].ge(minimum) & new["gap_listing_count"].lt(minimum)
                        & new["median_nightly_gap"].notna(), ["area_name", "airbnb_count", "gap_listing_count"]]
    test = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                           cwd=HERE, capture_output=True, text=True)
    (results / "test_results.txt").write_text(test.stdout + test.stderr, encoding="utf-8")
    assert test.returncode == 0, "Edge tests failed"
    checks["edge_tests_passed"] = True
    verification = dict(checks=checks, excluded_from_ranking=excluded.to_dict("records"),
                         old_eligible_locations=int((old.airbnb_count.ge(minimum) & old.median_nightly_gap.notna()).sum()),
                         new_eligible_locations=int((new.gap_listing_count.ge(minimum) & new.median_nightly_gap.notna()).sum()),
                         highest_rounded_gap_locations=ranked.loc[ranked.median_nightly_gap.round(2).eq(
                             ranked.median_nightly_gap.max().round(2)), "area_name"].tolist())
    (results / "verification_report.json").write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
