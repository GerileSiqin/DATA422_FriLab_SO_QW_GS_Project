"""Filter the June 2026 raw Airbnb data to Christchurch City only."""

from pathlib import Path
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np

# Find the deliverable_3 folder from the location of this Python script.
DELIVERABLE_DIR = Path(__file__).resolve().parents[1]

# Raw input file supplied for this task.
INPUT_FILE = DELIVERABLE_DIR / "Raw Data" / "listings-NZ-June26.csv"

# The filtered dataset will be saved in outputs.
OUTPUT_DIR = DELIVERABLE_DIR / "outputs" /"analysis_tables"
OUTPUT_FILE = OUTPUT_DIR / "Airbnb-Christchurch-lastreviewalltime.csv"

# Load the raw New Zealand listings data.
raw_data = pd.read_csv(INPUT_FILE, low_memory=False)

# Keep only rows where neighbourhood_group is Christchurch City.
christchurch_data = raw_data[
    raw_data["neighbourhood_group"] == "Christchurch City"
].copy()

# Create the output folder if it does not already exist.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Save the filtered rows without adding a pandas index column.
christchurch_data.to_csv(OUTPUT_FILE, index=False)

# Display a simple check in the terminal.
print("Raw NZ rows:", len(raw_data))
print("Christchurch City rows:", len(christchurch_data))
print("Filtered data saved to:", OUTPUT_FILE)


"""Filter the period of last review date between Oct 2025 and June 2026 with Christchurch City data only."""
"""the raw dataset only contains last review dates between 2019 and 2026, so we can filter the last review date to be between Oct 2025 and June 2026."""

# Raw input file supplied for this task.
INPUT_FILE_CHCH = DELIVERABLE_DIR / "outputs" / "analysis_tables" / "Airbnb-Christchurch-lastreviewalltime.csv"

# The filtered dataset will be saved in outputs/analysis_tables.
OUTPUT_DIR_CHCH = DELIVERABLE_DIR / "outputs" / "analysis_tables"
OUTPUT_FILE_CHCH = OUTPUT_DIR_CHCH / "Airbnb-Christchurch-oct25-jun26.csv"

# Load the raw Christchurch City listings data.
raw_data_chch = pd.read_csv(INPUT_FILE_CHCH, low_memory=False)

# Convert the last_review column to datetime format.
raw_data_chch["last_review"] = pd.to_datetime(raw_data_chch["last_review"], errors="coerce")

# filter the last_review column to be between Oct 2025 and June 2026.
filtered_data_chch = raw_data_chch[
    (raw_data_chch["last_review"] >= "2025-10-01") & (raw_data_chch["last_review"] <= "2026-06-30")
].copy()

# Create the output folder if it does not already exist.
OUTPUT_DIR_CHCH.mkdir(parents=True, exist_ok=True)

# Save the filtered rows without adding a pandas index column.
filtered_data_chch.to_csv(OUTPUT_FILE_CHCH, index=False)

# Display a simple check in the terminal.
print("Christchurch City Date rows:", len(raw_data_chch))
print("Filtered Christchurch City rows (Oct 2025 - June 2026):", len(filtered_data_chch))
print("Filtered data saved to:", OUTPUT_FILE_CHCH)


"""Add a new column called 'month_year' to the filtered date Christchurch City dataset."""
# Raw input file supplied for this task.
INPUT_FILE_CHCH_NCOL = DELIVERABLE_DIR / "outputs" / "analysis_tables" / "Airbnb-Christchurch-oct25-jun26.csv"

# The filtered dataset will be saved in outputs/analysis_tables.
OUTPUT_DIR_CHCH_NCOL = DELIVERABLE_DIR / "outputs" / "analysis_tables"
OUTPUT_FILE_CHCH_NCOL = OUTPUT_DIR_CHCH_NCOL / "Airbnb-Christchurch-oct25-jun26-ncol.csv"

# Load the Christchurch City Date listings data.
raw_data_chch_ncol = pd.read_csv(INPUT_FILE_CHCH_NCOL, low_memory=False)

# convert the last_review column to datetime format.
raw_data_chch_ncol["last_review"] = pd.to_datetime(raw_data_chch_ncol["last_review"], errors="coerce")

# add a new column called 'month_year' to the filtered date Christchurch City dataset in the first column.
raw_data_chch_ncol.insert(0, "month_year", raw_data_chch_ncol["last_review"].dt.to_period("M"))

# Create the output table.
OUTPUT_DIR_CHCH_NCOL.mkdir(parents=True, exist_ok=True)

# Save the file.
raw_data_chch_ncol.to_csv(OUTPUT_FILE_CHCH_NCOL, index=False)


"""Summary Statistics for all columns (categories + counts or min + max + mean + std) and number of missing values (per column) etc."""
# ------------------------------------------------------------
# 1. Define file locations
# ------------------------------------------------------------

DELIVERABLE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    DELIVERABLE_DIR
    / "outputs"
    / "analysis_tables"
    / "Airbnb-Christchurch-lastreviewalltime.csv"
)

SUMMARY_DIR = DELIVERABLE_DIR / "outputs" / "analysis_tables"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. Load the Christchurch dataset
# ------------------------------------------------------------

df = pd.read_csv(INPUT_FILE, low_memory=False)

print("Rows and columns:", df.shape)


# ------------------------------------------------------------
# 3. Missing values for every column
# ------------------------------------------------------------

missing_summary = pd.DataFrame({
    "column": df.columns,
    "missing_count": df.isna().sum().values,
    "missing_percent": (df.isna().mean().values * 100).round(2)
})

missing_summary.to_csv(
    SUMMARY_DIR / "missing_values_summary.csv",
    index=False
)

print("\nMissing values:")
print(missing_summary)


# ------------------------------------------------------------
# 4. Summary statistics for numeric columns
# ------------------------------------------------------------

numeric_columns = df.select_dtypes(include="number").columns

numeric_summary = df[numeric_columns].agg(
    ["count", "min", "max", "mean", "std"]
).T

numeric_summary["missing_count"] = df[numeric_columns].isna().sum()
numeric_summary["missing_percent"] = (
    df[numeric_columns].isna().mean() * 100
).round(2)

numeric_summary.to_csv(
    SUMMARY_DIR / "numeric_summary_statistics.csv"
)

print("\nNumeric summary:")
print(numeric_summary)


# ------------------------------------------------------------
# 5. Summary statistics for categorical columns
# ------------------------------------------------------------

categorical_columns = df.select_dtypes(
    include=["object", "category"]
).columns

categorical_summary_rows = []

for column in categorical_columns:
    category_counts = df[column].value_counts(dropna=False)

    for category, count in category_counts.items():
        categorical_summary_rows.append({
            "column": column,
            "category": category,
            "count": count
        })

categorical_summary = pd.DataFrame(categorical_summary_rows)

categorical_summary.to_csv(
    SUMMARY_DIR / "categorical_category_counts.csv",
    index=False
)

print("\nCategorical counts:")
print(categorical_summary)


# ------------------------------------------------------------
# 6. Display output location
# ------------------------------------------------------------

print("\nSummary tables saved to:")
print(SUMMARY_DIR)

#Plot the distribution of price as a histogram for both all data and Christchurch City data, and filtered Christchurch City data (Oct 2025 - June 2026).
"""Create the requested Deliverable 3 plots and top-review analysis."""

DELIVERABLE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = DELIVERABLE_DIR / "Raw Data" / "listings-NZ-June26.csv"
CHCH_FILE = (DELIVERABLE_DIR / "outputs" / "analysis_tables" / "Airbnb-Christchurch-lastreviewalltime.csv")
FILTERED_CHCH_FILE = (DELIVERABLE_DIR / "outputs" / "analysis_tables" / "Airbnb-Christchurch-oct25-jun26.csv")
OUTPUT_DIR = DELIVERABLE_DIR / "outputs" / "analysis_plots"
TABLE_DIR = DELIVERABLE_DIR / "outputs" / "analysis_tables"

# The June 2026 Inside Airbnb snapshot was scraped/published on 19 June 2026.
SCRAPE_DATE = pd.Timestamp("2026-06-19")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the three datasets used in the requested comparisons."""
    nz = pd.read_csv(RAW_FILE, low_memory=False)
    chch = pd.read_csv(CHCH_FILE, low_memory=False)
    filtered_chch = pd.read_csv(FILTERED_CHCH_FILE, low_memory=False)
    return nz, chch, filtered_chch


def plot_price_histograms(
    nz: pd.DataFrame,
    chch: pd.DataFrame,
    filtered_chch: pd.DataFrame,
) -> None:
    """Save separate and overlaid price-distribution histograms."""
    datasets = {
        "All New Zealand": nz,
        "Christchurch City": chch,
        "Christchurch: reviews Oct 2025–Jun 2026": filtered_chch,
    }

    # Prices cannot be negative. Calculate the shared range from valid,
    # non-negative NZ prices only, then apply the same rule to every dataset.
    valid_nz_prices = pd.to_numeric(nz["price"], errors="coerce")
    valid_nz_prices = valid_nz_prices[valid_nz_prices.ge(0)]

    # A few extreme prices compress the main distribution. Use a shared upper
    # limit based on the 99th percentile of valid NZ prices, and report it.
    upper_limit = valid_nz_prices.quantile(0.99)
    bins = np.linspace(0, upper_limit, 51)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharex=True)
    colors = ["#2563A5", "#D68A24", "#7A8B3A"]

    for axis, (label, data), color in zip(axes, datasets.items(), colors):
        numeric_prices = pd.to_numeric(data["price"], errors="coerce")
        prices = numeric_prices[numeric_prices.between(0, upper_limit)]
        axis.hist(prices, bins=bins, color=color, edgecolor="white")
        axis.set_title(label)
        axis.set_xlabel("Nightly price (NZD)")
        axis.set_ylabel("Number of listings")
        axis.set_xlim(0, upper_limit)
        axis.set_ylim(bottom=0)
        axis.grid(axis="y", alpha=0.2)

    fig.suptitle("Airbnb Price Distributions")
    fig.text(
        0.5,
        0.01,
        f"Shared range: NZ$0–{upper_limit:,.0f} (99th percentile of NZ prices)",
        ha="center",
    )
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    fig.savefig(OUTPUT_DIR / "01_price_histograms_separate.png", dpi=300)
    plt.close(fig)

    # Plot all three distributions together using density so datasets with
    # different row counts can be compared fairly.
    fig, axis = plt.subplots(figsize=(10, 6))
    for (label, data), color in zip(datasets.items(), colors):
        numeric_prices = pd.to_numeric(data["price"], errors="coerce")
        prices = numeric_prices[numeric_prices.between(0, upper_limit)]
        axis.hist(
            prices,
            bins=bins,
            density=True,
            histtype="step",
            linewidth=2,
            label=f"{label} (n={len(prices):,})",
            color=color,
        )

    axis.set_title("Airbnb Price Distributions: New Zealand and Christchurch")
    axis.set_xlabel("Nightly price (NZD)")
    axis.set_ylabel("Density")
    axis.set_xlim(0, upper_limit)
    axis.set_ylim(bottom=0)
    axis.grid(axis="y", alpha=0.2)
    axis.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "02_price_histograms_combined.png", dpi=300)
    plt.close(fig)

    print(f"Price plots use NZ$0–{upper_limit:,.2f}, the NZ 99th percentile.")


def plot_days_since_last_review(chch: pd.DataFrame) -> None:
    """Calculate and plot days between scrape date and last review."""
    review_data = chch.copy()
    review_data["last_review"] = pd.to_datetime(
        review_data["last_review"], errors="coerce"
    )
    review_data["days_since_last_review"] = (
        SCRAPE_DATE - review_data["last_review"]
    ).dt.days

    # Remove missing dates and impossible future-review values from both the
    # plots and the exported plot-data table.
    invalid_review_count = int(
        review_data["days_since_last_review"].lt(0).sum()
    )
    valid_review_data = review_data.loc[
        review_data["days_since_last_review"].ge(0)
    ].copy()
    plot_data = valid_review_data["days_since_last_review"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].hist(plot_data, bins=50, color="#2563A5", edgecolor="white")
    axes[0].set_title("Complete distribution")
    axes[0].set_xlabel("Days since last review")
    axes[0].set_ylabel("Number of listings")
    axes[0].set_xlim(left=0)
    axes[0].set_ylim(bottom=0)
    axes[0].grid(axis="y", alpha=0.2)

    recent_data = plot_data[plot_data <= 365]
    axes[1].hist(recent_data, bins=30, color="#D68A24", edgecolor="white")
    axes[1].set_title("Closer view: last 365 days")
    axes[1].set_xlabel("Days since last review")
    axes[1].set_ylabel("Number of listings")
    axes[1].set_xlim(0, 365)
    axes[1].set_ylim(bottom=0)
    axes[1].grid(axis="y", alpha=0.2)

    fig.suptitle("Days Since Last Review for Christchurch Listings")
    fig.text(
        0.5,
        0.01,
        "Calculated from the 19 June 2026 scrape date; missing or future-dated reviews are excluded",
        ha="center",
    )
    fig.tight_layout(rect=[0, 0.05, 1, 0.94])
    fig.savefig(OUTPUT_DIR / "03_days_since_last_review.png", dpi=300)
    plt.close(fig)

    valid_review_data.to_csv(
        TABLE_DIR / "christchurch_with_days_since_last_review.csv", index=False
    )
    print(f"Future-dated reviews excluded: {invalid_review_count:,}")
    print(f"Listings plotted for days since last review: {len(plot_data):,}")


def find_top_reviewed_properties(nz: pd.DataFrame) -> None:
    """Find the top 10% of NZ listings by all-time number of reviews."""
    review_counts = nz["number_of_reviews"].dropna()
    threshold = review_counts.quantile(0.90)
    top_reviewed = nz.loc[nz["number_of_reviews"].ge(threshold)].copy()
    top_reviewed = top_reviewed.sort_values(
        ["number_of_reviews", "id"], ascending=[False, True]
    )

    christchurch_top = top_reviewed[
        top_reviewed["neighbourhood_group"].eq("Christchurch City")
    ]

    columns = [
        "id",
        "name",
        "host_name",
        "neighbourhood_group",
        "neighbourhood",
        "room_type",
        "price",
        "number_of_reviews",
    ]
    top_reviewed[columns].to_csv(
        TABLE_DIR / "nz_properties_top_10_percent_reviews.csv", index=False
    )
    christchurch_top[columns].to_csv(
        TABLE_DIR / "christchurch_properties_in_nz_top_10_percent_reviews.csv",
        index=False,
    )

    print(f"NZ top-10% review threshold: {threshold:g} reviews")
    print(f"NZ listings meeting threshold: {len(top_reviewed):,}")
    print(f"Of these, Christchurch City listings: {len(christchurch_top):,}")
    print("Highest-reviewed NZ properties:")
    print(top_reviewed[columns].head(10).to_string(index=False))


def main() -> None:
    nz, chch, filtered_chch = load_data()
    plot_price_histograms(nz, chch, filtered_chch)
    plot_days_since_last_review(chch)
    find_top_reviewed_properties(nz)
    print(f"\nPlots saved to: {OUTPUT_DIR}")
    print(f"Analysis tables saved to: {TABLE_DIR}")


if __name__ == "__main__":
    main()

#Find out which properties in NZ get the highest number of reviews (top 10%), and how many of those are in Christchurch City. Save the results to a CSV file.
""""""
review_threshold = raw_data["number_of_reviews"].quantile(0.90)

top_10_percent = raw_data[
    raw_data["number_of_reviews"] >= review_threshold
].copy()

top_10_percent = top_10_percent.sort_values(
    "number_of_reviews",
    ascending=False
)

christchurch_top_10 = top_10_percent[
    top_10_percent["neighbourhood_group"] == "Christchurch City"
]

print("Review threshold:", review_threshold)
print("NZ properties in top 10%:", len(top_10_percent))
print("Properties in Christchurch:", len(christchurch_top_10))
