"""Create the Deliverable 3 plots and their supporting CSV tables."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# 1. Project folders
# -----------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PROCESSED = PROJECT_ROOT / "deliverable_3" / "data_processed"
OUTPUTS = PROJECT_ROOT / "deliverable_3" / "outputs"

PLOTS = OUTPUTS / "plots"
PLOT_DATA = OUTPUTS / "plot_data"

PLOTS.mkdir(parents=True, exist_ok=True)
PLOT_DATA.mkdir(parents=True, exist_ok=True)


def save_plot(filename: str) -> Path:
    """Save and close the current Matplotlib figure."""
    output_file = PLOTS / filename
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_file}")
    return output_file


# -----------------------------------------------------------------------------
# 2. Load and validate the Christchurch dataset
# -----------------------------------------------------------------------------

input_file = DATA_PROCESSED / "christchurch_airbnb_oct2025_jun2026.csv"

if not input_file.is_file():
    raise FileNotFoundError(
        f"Input dataset was not found: {input_file}"
    )

df = pd.read_csv(input_file)

required_columns = {
    "id",
    "name",
    "room_type",
    "price",
    "last_review",
    "month_year",
    "number_of_reviews",
}

missing_columns = required_columns.difference(df.columns)

if missing_columns:
    raise ValueError(
        "Dataset is missing required columns: "
        + ", ".join(sorted(missing_columns))
    )

# Convert numeric fields.
# Invalid text becomes missing instead of causing errors.
df["price"] = pd.to_numeric(
    df["price"],
    errors="coerce"
)

df["number_of_reviews"] = pd.to_numeric(
    df["number_of_reviews"],
    errors="coerce"
)

print("Combined Christchurch dataset loaded.")
print("Rows and columns:", df.shape)


# -----------------------------------------------------------------------------
# 3. Plot 1: Listings with a last review by month
# -----------------------------------------------------------------------------

# This measures listings by the month of their most recent review.
review_months = pd.period_range(
    "2025-10",
    "2026-06",
    freq="M"
).astype(str)

plot1_data = df[
    ["id", "last_review"]
].copy()

plot1_data["last_review"] = pd.to_datetime(
    plot1_data["last_review"],
    errors="coerce"
)

# Keep only valid review dates in the required period.
plot1_data = plot1_data[
    plot1_data["last_review"].between(
        "2025-10-01",
        "2026-06-30"
    )
].copy()

plot1_data["review_month"] = (
    plot1_data["last_review"]
    .dt.to_period("M")
    .astype(str)
)

listings_by_month = (
    plot1_data
    .groupby("review_month")["id"]
    .nunique()
    .reindex(review_months, fill_value=0)
    .rename_axis("review_month")
    .rename("listing_count")
    .reset_index()
)

plt.figure(figsize=(8, 6))

bars = plt.bar(
    listings_by_month["review_month"],
    listings_by_month["listing_count"],
    width=0.7,
)

# Add the exact number above each bar.
for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{int(height):,}",
        ha="center",
        va="bottom",
    )

plt.title(
    "Christchurch Listings with a Last Review by Month"
)

plt.figtext(
    0.5,
    0.91,
    "October 2025-June 2026, based on the combined dataset",
    ha="center",
    fontsize=10,
)

plt.xlabel("Month of last review")
plt.ylabel("Number of listings")
plt.ylim(bottom=0)
plt.grid(axis="y", alpha=0.2)
plt.tight_layout(rect=[0, 0, 1, 0.90])

save_plot("01_listings_by_month.png")

listings_by_month.to_csv(
    PLOT_DATA / "plot_listings_by_month_data.csv",
    index=False
)


# -----------------------------------------------------------------------------
# 4. Plot 2: Room type counts
# -----------------------------------------------------------------------------

room_type_counts = (
    df["room_type"]
    .fillna("Missing")
    .value_counts()
    .rename_axis("room_type")
    .rename("count")
    .reset_index()
)

plt.figure(figsize=(8, 6))

bars = plt.bar(
    room_type_counts["room_type"],
    room_type_counts["count"]
)

for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{int(height):,}",
        ha="center",
        va="bottom",
    )

plt.title(
    "Christchurch Airbnb Listings by Room Type"
)

plt.xlabel("Room type")
plt.ylabel("Number of listings")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

save_plot("02_room_type_counts.png")

room_type_counts.to_csv(
    PLOT_DATA / "plot_room_type_counts_data.csv",
    index=False
)


# -----------------------------------------------------------------------------
# 5. Plot 3: Price distribution using custom bins
# -----------------------------------------------------------------------------

# Keep only valid, non-negative prices.
price_data = df[
    df["price"].notna()
    & df["price"].ge(0)
].copy()

price_bins = [
    0,
    50,
    150,
    250,
    350,
    450,
    550,
    650,
    750,
    850,
    950,
    np.inf,
]

price_labels = [
    "< 50",
    "50-150",
    "150-250",
    "250-350",
    "350-450",
    "450-550",
    "550-650",
    "650-750",
    "750-850",
    "850-950",
    ">= 950",
]

# right=False:
# left boundary is included,
# right boundary is excluded.
price_data["price_group"] = pd.cut(
    price_data["price"],
    bins=price_bins,
    labels=price_labels,
    right=False,
    include_lowest=True,
)

price_group_counts = (
    price_data["price_group"]
    .value_counts(sort=False)
    .reindex(price_labels, fill_value=0)
    .rename_axis("price_group")
    .rename("count")
    .reset_index()
)

price_950_or_more_count = int(
    price_data["price"]
    .ge(950)
    .sum()
)

print("\nPrice distribution:")
print(
    price_group_counts.to_string(index=False)
)

print(
    "Listings with price >= 950:",
    price_950_or_more_count
)

plt.figure(figsize=(10, 6))

bars = plt.bar(
    price_group_counts["price_group"],
    price_group_counts["count"]
)

for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{int(height):,}",
        ha="center",
        va="bottom",
    )

plt.title(
    "Christchurch Airbnb Price Distribution"
)

plt.xlabel("Price group")
plt.ylabel("Number of listings")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

save_plot(
    "03_price_distribution_custom_bins.png"
)

price_group_counts.to_csv(
    PLOT_DATA / "price_group_counts.csv",
    index=False
)


# -----------------------------------------------------------------------------
# 6. Plot 4: Days since last review
# -----------------------------------------------------------------------------

scrape_dates = {
    "2025-10": "2025-10-05",
    "2025-11": "2025-11-07",
    "2025-12": "2025-12-11",
    "2026-01": "2026-01-16",
    "2026-02": "2026-02-13",
    "2026-03": "2026-03-17",
    "2026-04": "2026-04-16",
    "2026-05": "2026-05-23",
    "2026-06": "2026-06-19",
}

review_data = df[
    [
        "id",
        "name",
        "month_year",
        "last_review"
    ]
].copy()

review_data["last_review"] = pd.to_datetime(
    review_data["last_review"],
    errors="coerce"
)

review_data["scrape_date"] = pd.to_datetime(
    review_data["month_year"]
    .astype(str)
    .map(scrape_dates),
    errors="coerce"
)

missing_review_dates = int(
    review_data["last_review"]
    .isna()
    .sum()
)

missing_scrape_dates = int(
    review_data["scrape_date"]
    .isna()
    .sum()
)

# Exclude rows where either required date is missing.
review_data = review_data.dropna(
    subset=[
        "last_review",
        "scrape_date"
    ]
).copy()

review_data["days_since_last_review"] = (
    review_data["scrape_date"]
    - review_data["last_review"]
).dt.days

# Remove future-dated reviews.
future_review_count = int(
    review_data["days_since_last_review"]
    .lt(0)
    .sum()
)

review_data = review_data[
    review_data["days_since_last_review"]
    .ge(0)
].copy()

print(
    "\nRows with missing/invalid last_review:",
    missing_review_dates
)

print(
    "Rows with an unmapped month_year:",
    missing_scrape_dates
)

print(
    "Future-dated reviews excluded from Plot 4:",
    future_review_count
)

if review_data.empty:
    raise ValueError(
        "No valid rows remain for the days-since-last-review plot."
    )

plt.figure(figsize=(10, 6))

counts, bin_edges, patches = plt.hist(
    review_data["days_since_last_review"],
    bins=50
)

max_index = int(
    np.argmax(counts)
)

max_count = int(
    counts[max_index]
)

max_bar = patches[max_index]

max_bin_left = bin_edges[max_index]
max_bin_right = bin_edges[max_index + 1]

# Add the count above the highest histogram bar.
plt.text(
    max_bar.get_x()
    + max_bar.get_width() / 2,
    max_count,
    f"{max_count:,}",
    ha="center",
    va="bottom",
)

plt.title(
    "Days Since Last Review for Christchurch Listings"
)

plt.xlabel("Days since last review")
plt.ylabel("Number of listings")
plt.xlim(left=0)
plt.grid(axis="y", alpha=0.2)
plt.tight_layout()

save_plot(
    "04_days_since_last_review_distribution.png"
)

print(
    "\nHighest bar in days-since-last-review histogram:"
)

print(
    f"{max_bin_left:.1f} to "
    f"{max_bin_right:.1f} days: "
    f"{max_count}"
)

review_data.to_csv(
    PLOT_DATA / "days_since_last_review.csv",
    index=False
)


# -----------------------------------------------------------------------------
# 7. Plot 5: Top 10% most-reviewed Christchurch listings
# -----------------------------------------------------------------------------

# Keep only rows with a valid review count.
reviews_data = df[
    df["number_of_reviews"].notna()
].copy()

if reviews_data.empty:
    raise ValueError(
        "No valid number_of_reviews values are available for Plot 5."
    )

# Calculate the number of listings in the top 10%.
top_n = max(
    1,
    int(
        np.ceil(
            len(reviews_data) * 0.10
        )
    )
)

# Sort from highest to lowest number of reviews.
top_10_reviews = (
    reviews_data
    .sort_values(
        "number_of_reviews",
        ascending=False
    )
    .head(top_n)
    .copy()
)

cutoff_reviews = (
    top_10_reviews["number_of_reviews"]
    .min()
)

print(
    "\nTop 10% most-reviewed Christchurch listings:"
)

print(
    "Total listings with review counts:",
    len(reviews_data)
)

print(
    "Top 10% listings:",
    len(top_10_reviews)
)

print(
    "Cutoff number_of_reviews:",
    cutoff_reviews
)

top_room_type_counts = (
    top_10_reviews["room_type"]
    .fillna("Missing")
    .value_counts()
    .rename_axis("room_type")
    .rename("count")
    .reset_index()
)

plt.figure(figsize=(8, 6))

bars = plt.bar(
    top_room_type_counts["room_type"],
    top_room_type_counts["count"]
)

for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{int(height):,}",
        ha="center",
        va="bottom",
    )

plt.title(
    "Top 10% Most-Reviewed Christchurch Listings by Room Type"
)

plt.xlabel("Room type")
plt.ylabel("Number of listings")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

save_plot(
    "05_top_10_percent_reviews_by_room_type.png"
)

top_10_reviews.to_csv(
    PLOT_DATA
    / "top_10_percent_most_reviewed_christchurch.csv",
    index=False
)

top_room_type_counts.to_csv(
    PLOT_DATA
    / "top_10_percent_room_type_counts.csv",
    index=False
)


# -----------------------------------------------------------------------------
# 8. Finish
# -----------------------------------------------------------------------------

print("\nAll plots saved to:")
print(PLOTS)

print("\nPlot data CSV files saved to:")
print(PLOT_DATA)