"""Tutor demonstration: validate persisted joins and hand-check one calculation."""

import argparse
import json
from pathlib import Path

import pandas as pd

from pipeline.validation import sanity_check


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path(__file__).resolve().parent / "results")
    args = parser.parse_args()
    folder = args.results / "data_processed"
    airbnb = pd.read_csv(folder / "airbnb_prepared.csv", parse_dates=["snapshot_date", "bond_time"])
    joined = pd.read_csv(folder / "airbnb_bond_joined.csv", parse_dates=["snapshot_date", "bond_time"])
    summary = pd.read_csv(folder / "location_comparison.csv", parse_dates=["bond_time"])
    quality = sanity_check(airbnb, joined, summary)
    sample = joined.dropna(subset=["price", "median_weekly_rent"]).iloc[0]
    example = dict(id=int(sample["id"]), snapshot_date=f"{sample['snapshot_date']:%Y-%m-%d}",
                   quarter=f"{sample['bond_time']:%Y-%m-%d}", nightly_price=float(sample["price"]),
                   weekly_rent=float(sample["median_weekly_rent"]),
                   expected_gap=float(sample["price"] - sample["median_weekly_rent"] / 7.0),
                   saved_gap=float(sample["nightly_price_gap"]))
    result = dict(quality=quality, example=example)
    (args.results / "sanity_check_example.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
