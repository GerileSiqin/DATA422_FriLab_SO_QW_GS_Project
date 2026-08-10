# 03_create_plots.py
# Purpose:
# Reproduce the previous Orange/no-code workflow and plots in Python.
# This script uses pandas for data processing,
# numpy for numeric tools,
# and matplotlib for plotting.
#
# Output folders:
# deliverable_3/outputs/plots/      = final plot images
# deliverable_3/outputs/plot_data/  = small CSV tables used to make plots

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------
# 1. Define project folders
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PROCESSED = PROJECT_ROOT / "deliverable_3" / "data_processed"
OUTPUTS = PROJECT_ROOT / "deliverable_3" / "outputs"

# Organised output folders
PLOTS = OUTPUTS / "plots"
PLOT_DATA = OUTPUTS / "plot_data"

# Create output folders if they do not already exist
OUTPUTS.mkdir(parents=True, exist_ok=True)
PLOTS.mkdir(parents=True, exist_ok=True)
PLOT_DATA.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# 2. Load combined Christchurch dataset
# ------------------------------------------------------------

input_file = DATA_PROCESSED / "christchurch_airbnb_oct2025_jun2026.csv"

df = pd.read_csv(input_file)

print("Combined Christchurch dataset loaded.")
print("Rows and columns:", df.shape)

# ------------------------------------------------------------
# 3. Plot 1: Listings by month
# ------------------------------------------------------------

listings_by_month = (
    df["month_year"]
    .value_counts()
    .sort_index()
    .reset_index()
)

listings_by_month.columns = ["month_year", "listing_count"]

plt.figure(figsize=(10, 6))

plt.plot(
    listings_by_month["month_year"],
    listings_by_month["listing_count"],
    marker="o"
)

# Add exact number above each dot.
for x, y in zip(listings_by_month["month_year"], listings_by_month["listing_count"]):
    plt.text(
        x,
        y,
        str(y),
        ha="center",
        va="bottom"
    )

plt.title("Christchurch Airbnb Listings by Month")
plt.xlabel("Month")
plt.ylabel("Number of listings")
plt.xticks(rotation=45)
plt.tight_layout()

output_file = PLOTS / "01_listings_by_month.png"
plt.savefig(output_file, dpi=300)
plt.close()

print("Saved:", output_file)

# Save the data used to make this plot.
listings_by_month.to_csv(
    PLOT_DATA / "plot_listings_by_month_data.csv",
    index=False
)

# ------------------------------------------------------------
# 4. Plot 2: Room type counts
# ------------------------------------------------------------

room_type_counts = (
    df["room_type"]
    .value_counts(dropna=False)
    .reset_index()
)

room_type_counts.columns = ["room_type", "count"]

plt.figure(figsize=(8, 6))

bars = plt.bar(
    room_type_counts["room_type"],
    room_type_counts["count"]
)

# Add exact number above each bar.
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        str(int(height)),
        ha="center",
        va="bottom"
    )

plt.title("Christchurch Airbnb Listings by Room Type")
plt.xlabel("Room type")
plt.ylabel("Number of listings")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

output_file = PLOTS / "02_room_type_counts.png"
plt.savefig(output_file, dpi=300)
plt.close()

print("Saved:", output_file)

room_type_counts.to_csv(
    PLOT_DATA / "plot_room_type_counts_data.csv",
    index=False
)

# ------------------------------------------------------------
# 5. Plot 3: Price distribution using custom bins
# ------------------------------------------------------------

# This reproduces the Discretize custom-bin idea from Orange.
# We keep rows where price is defined.
price_data = df[df["price"].notna()].copy()

# Custom price groups.
# np.inf means infinity, so the final group includes all prices >= 1000.
price_bins = [0, 50, 100, 150, 200, 300, 500, 1000, np.inf]

price_labels = [
    "< 50",
    "50–100",
    "100–150",
    "150–200",
    "200–300",
    "300–500",
    "500–1000",
    "≥ 1000"
]

# pd.cut() converts numeric price values into price groups.
# right=False means 50–100 means 50 <= price < 100.
price_data["price_group"] = pd.cut(
    price_data["price"],
    bins=price_bins,
    labels=price_labels,
    right=False
)

price_group_counts = (
    price_data["price_group"]
    .value_counts()
    .reindex(price_labels)
    .reset_index()
)

price_group_counts.columns = ["price_group", "count"]

# Check how many listings have price >= 1000.
price_over_1000_count = int((price_data["price"] >= 1000).sum())

print("\nPrice distribution:")
print(price_group_counts)
print("Listings with price >= 1000:", price_over_1000_count)

plt.figure(figsize=(10, 6))

bars = plt.bar(
    price_group_counts["price_group"],
    price_group_counts["count"]
)

# Add exact number above each bar.
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        str(int(height)),
        ha="center",
        va="bottom"
    )

plt.title("Christchurch Airbnb Price Distribution")
plt.xlabel("Price group")
plt.ylabel("Number of listings")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

output_file = PLOTS / "03_price_distribution_custom_bins.png"
plt.savefig(output_file, dpi=300)
plt.close()

print("Saved:", output_file)

price_group_counts.to_csv(
    PLOT_DATA / "price_group_counts.csv",
    index=False
)

# ------------------------------------------------------------
# 6. Plot 4: Days since last review
# ------------------------------------------------------------

# This reproduces the days_since_last_review idea from Orange.
# The scrape dates come from the downloaded file dates.
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

# Keep only rows where last_review is not missing.
review_data = df[df["last_review"].notna()].copy()

# Add scrape date using month_year.
review_data["scrape_date"] = review_data["month_year"].map(scrape_dates)

# Convert date text into datetime objects.
review_data["last_review"] = pd.to_datetime(review_data["last_review"])
review_data["scrape_date"] = pd.to_datetime(review_data["scrape_date"])

# Calculate days since last review.
review_data["days_since_last_review"] = (
    review_data["scrape_date"] - review_data["last_review"]
).dt.days

plt.figure(figsize=(10, 6))

# plt.hist returns:
# counts = number of listings in each bin
# bins = bin boundaries
# patches = bar objects
counts, bins, patches = plt.hist(
    review_data["days_since_last_review"],
    bins=50
)

# Find the highest histogram bar.
max_count = int(counts.max())
max_index = int(counts.argmax())
max_bar = patches[max_index]

max_bin_left = bins[max_index]
max_bin_right = bins[max_index + 1]

# Add exact number above the highest bar.
plt.text(
    max_bar.get_x() + max_bar.get_width() / 2,
    max_count,
    str(max_count),
    ha="center",
    va="bottom"
)

plt.title("Days Since Last Review for Christchurch Listings")
plt.xlabel("Days since last review")
plt.ylabel("Number of listings")
plt.tight_layout()

output_file = PLOTS / "04_days_since_last_review_distribution.png"
plt.savefig(output_file, dpi=300)
plt.close()

print("Saved:", output_file)

print("\nHighest bar in days_since_last_review histogram:")
print(f"{max_bin_left:.1f} to {max_bin_right:.1f} days:", max_count)

# Save data used for the days-since-last-review plot.
review_data[[
    "id",
    "name",
    "month_year",
    "last_review",
    "scrape_date",
    "days_since_last_review"
]].to_csv(
    PLOT_DATA / "days_since_last_review.csv",
    index=False
)

# ------------------------------------------------------------
# 7. Plot 5: Top 10% most-reviewed Christchurch listings
# ------------------------------------------------------------

# Since Deliverable 3 uses Christchurch data only,
# this finds the top 10% within Christchurch.
reviews_data = df[df["number_of_reviews"].notna()].copy()

# Calculate 10% of Christchurch listings.
top_n = int(np.ceil(len(reviews_data) * 0.10))

# Sort listings by number_of_reviews from highest to lowest.
reviews_data_sorted = reviews_data.sort_values(
    by="number_of_reviews",
    ascending=False
)

# Select the top 10%.
top_10_reviews = reviews_data_sorted.head(top_n).copy()

# Cutoff = the smallest number_of_reviews in the top 10%.
cutoff_reviews = top_10_reviews["number_of_reviews"].min()

print("\nTop 10% most-reviewed Christchurch listings:")
print("Total Christchurch listings with review counts:", len(reviews_data))
print("Top 10% listings:", len(top_10_reviews))
print("Cutoff number_of_reviews:", cutoff_reviews)

# Count room types within the top 10% most-reviewed listings.
top_room_type_counts = (
    top_10_reviews["room_type"]
    .value_counts(dropna=False)
    .reset_index()
)

top_room_type_counts.columns = ["room_type", "count"]

plt.figure(figsize=(8, 6))

bars = plt.bar(
    top_room_type_counts["room_type"],
    top_room_type_counts["count"]
)

# Add exact number above each bar.
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        str(int(height)),
        ha="center",
        va="bottom"
    )

plt.title("Top 10% Most-Reviewed Christchurch Listings by Room Type")
plt.xlabel("Room type")
plt.ylabel("Number of listings")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

output_file = PLOTS / "05_top_10_percent_reviews_by_room_type.png"
plt.savefig(output_file, dpi=300)
plt.close()

print("Saved:", output_file)

# Save top 10% output data.
top_10_reviews.to_csv(
    PLOT_DATA / "top_10_percent_most_reviewed_christchurch.csv",
    index=False
)

top_room_type_counts.to_csv(
    PLOT_DATA / "top_10_percent_room_type_counts.csv",
    index=False
)

print("\nAll plots saved to:")
print(PLOTS)

print("\nPlot data CSV files saved to:")
print(PLOT_DATA)