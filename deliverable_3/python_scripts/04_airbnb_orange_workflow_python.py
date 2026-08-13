"""Python equivalent of the Orange workflow Airbnb-Christchurch-NZ.ows.

The script reproduces the workflow's filters, derived column, summary tables,
price distributions, days-since-last-review plots, and top-10%-review tables.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CHRISTCHURCH = "Christchurch City"


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    deliverable_dir = script_dir.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=deliverable_dir / "Raw Data" / "listings-NZ-June26.csv",
        help="New Zealand Airbnb listings CSV",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=deliverable_dir / "outputs" / "orange_workflow_python",
        help="Folder for tables and plots",
    )
    parser.add_argument(
        "--as-of",
        type=pd.Timestamp,
        default=pd.Timestamp.today().normalize(),
        help="Date used for days_since_last_review (default: today)",
    )
    return parser.parse_args()


def load_listings(path: Path) -> pd.DataFrame:
    """Orange File widget: load the source data and validate required fields."""
    data = pd.read_csv(path, low_memory=False)
    required = {"neighbourhood_group", "price", "last_review", "number_of_reviews"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    data["last_review"] = pd.to_datetime(data["last_review"], errors="coerce")
    return data


def add_days_since_last_review(data: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Orange Python Script widget: add days_since_last_review."""
    result = data.copy()
    result["days_since_last_review"] = (as_of - result["last_review"]).dt.days
    return result


def save_table(data: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)


def save_price_histogram(data: pd.DataFrame, upper: float | None, path: Path, title: str) -> None:
    """Orange Distributions widget equivalent for the price column."""
    prices = data["price"].dropna()
    if upper is not None:
        prices = prices[prices < upper]
    fig, axis = plt.subplots(figsize=(9, 6))
    axis.hist(prices, bins=40, color="#2878B5", edgecolor="white")
    axis.set(title=title, xlabel="Nightly price (NZD)", ylabel="Number of listings")
    axis.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def save_days_histogram(data: pd.DataFrame, path: Path, title: str) -> None:
    values = data["days_since_last_review"].dropna()
    values = values[values >= 0]
    fig, axis = plt.subplots(figsize=(9, 6))
    axis.hist(values, bins=40, color="#D67B28", edgecolor="white")
    axis.set(title=title, xlabel="Days since last review", ylabel="Number of listings")
    axis.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    output = args.output_dir.resolve()
    tables = output / "tables"
    plots = output / "plots"
    tables.mkdir(parents=True, exist_ok=True)
    plots.mkdir(parents=True, exist_ok=True)

    # Orange: File -> Select Rows (Christchurch) -> Data Table.
    nz = load_listings(args.input)
    christchurch = nz[nz["neighbourhood_group"].eq(CHRISTCHURCH)].copy()
    save_table(christchurch, tables / "christchurch_data.csv")

    # Orange: Select Columns (Price) -> Statistics / filters / distributions.
    christchurch[["price"]].describe().T.to_csv(tables / "christchurch_price_summary.csv")
    nz[["price"]].describe().T.to_csv(tables / "nz_price_summary.csv")

    chch_price_below_500 = christchurch[christchurch["price"].lt(500)].copy()
    nz_price_below_1000 = nz[nz["price"].lt(1000)].copy()
    save_table(chch_price_below_500, tables / "christchurch_price_below_500.csv")
    save_table(nz_price_below_1000, tables / "nz_price_below_1000.csv")
    save_price_histogram(christchurch, None, plots / "christchurch_all_prices.png", "Christchurch: all prices")
    save_price_histogram(christchurch, 500, plots / "christchurch_prices_below_500.png", "Christchurch prices below NZ$500")
    save_price_histogram(nz, None, plots / "nz_all_prices.png", "New Zealand: all prices")
    save_price_histogram(nz, 1000, plots / "nz_prices_below_1000.png", "New Zealand prices below NZ$1,000")

    # Orange Python Script: calculate days from last review to the chosen date.
    nz_with_days = add_days_since_last_review(nz, args.as_of)
    save_table(nz_with_days, tables / "nz_with_days_since_last_review.csv")
    save_days_histogram(nz_with_days, plots / "nz_days_since_last_review.png", "New Zealand: days since last review")

    # Orange branch: price < 1000 and last_review from 2021-08-01 onward.
    recent_below_1000 = nz[
        nz["price"].lt(1000) & nz["last_review"].ge(pd.Timestamp("2021-08-01"))
    ].copy()
    recent_below_1000 = add_days_since_last_review(recent_below_1000, args.as_of)
    save_table(recent_below_1000, tables / "nz_price_below_1000_reviews_since_2021_08_01.csv")
    save_days_histogram(
        recent_below_1000,
        plots / "nz_recent_price_below_1000_days_since_review.png",
        "NZ listings below $1,000 with reviews since 1 Aug 2021",
    )

    # Orange Discretize (10 equal-frequency groups) -> top review decile.
    threshold = nz["number_of_reviews"].quantile(0.90)
    top_reviews = nz[nz["number_of_reviews"].ge(threshold)].copy()
    top_reviews = top_reviews.sort_values("number_of_reviews", ascending=False)
    christchurch_top_reviews = top_reviews[
        top_reviews["neighbourhood_group"].eq(CHRISTCHURCH)
    ].copy()
    save_table(top_reviews, tables / "nz_top_10_percent_by_reviews.csv")
    save_table(christchurch_top_reviews, tables / "christchurch_in_nz_top_10_percent_reviews.csv")

    print(f"Input rows: {len(nz):,}")
    print(f"Christchurch rows: {len(christchurch):,}")
    print(f"Top-10% review threshold: {threshold:g}")
    print(f"NZ listings in top group: {len(top_reviews):,}")
    print(f"Christchurch listings in top group: {len(christchurch_top_reviews):,}")
    print(f"Outputs saved to: {output}")


if __name__ == "__main__":
    main()
