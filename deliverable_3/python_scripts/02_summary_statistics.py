# 02_summary_statistics.py
# Purpose:
# Load the combined Christchurch Airbnb dataset,
# calculate missing values and numeric summary statistics,
# and create useful project-specific summaries.
#
# Main output folder:
# deliverable_3/outputs/summary_tables/

from pathlib import Path
import pandas as pd

# ------------------------------------------------------------
# 1. Define project folders
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PROCESSED = PROJECT_ROOT / "deliverable_3" / "data_processed"
OUTPUTS = PROJECT_ROOT / "deliverable_3" / "outputs"

# New organised output folder for summary CSV files
SUMMARY_TABLES = OUTPUTS / "summary_tables"

# Create output folders if they do not already exist
OUTPUTS.mkdir(parents=True, exist_ok=True)
SUMMARY_TABLES.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# 2. Load combined Christchurch dataset
# ------------------------------------------------------------

input_file = DATA_PROCESSED / "christchurch_airbnb_oct2025_jun2026.csv"

df = pd.read_csv(input_file)

print("Combined Christchurch dataset loaded.")
print("Rows and columns:", df.shape)

# ------------------------------------------------------------
# 3. Missing values per column
# ------------------------------------------------------------

# df.isna() checks missing values.
# df.isna().sum() counts missing values per column.
# missing_percent shows the percentage of missing values in each column.
missing_summary = pd.DataFrame({
    "column": df.columns,
    "missing_count": df.isna().sum().values,
    "missing_percent": (df.isna().sum().values / len(df) * 100).round(2)
})

print("\nMissing values per column:")
print(missing_summary)

missing_output = SUMMARY_TABLES / "missing_values_summary.csv"
missing_summary.to_csv(missing_output, index=False)

# ------------------------------------------------------------
# 4. Numeric summary statistics
# ------------------------------------------------------------

# Only include numeric columns where summary statistics
# such as mean, standard deviation, min and max are meaningful.
numeric_columns = [
    "price",
    "minimum_nights",
    "number_of_reviews",
    "reviews_per_month",
    "calculated_host_listings_count",
    "availability_365",
    "number_of_reviews_ltm"
]

# Calculate count, mean, std, min, quartiles, and max.
numeric_summary = df[numeric_columns].describe().T

print("\nNumeric summary statistics:")
print(numeric_summary)

numeric_output = SUMMARY_TABLES / "numeric_summary_statistics.csv"
numeric_summary.to_csv(numeric_output)

# ------------------------------------------------------------
# 5. Useful project-specific summaries
# ------------------------------------------------------------

print("\nListings by month:")
print(df["month_year"].value_counts().sort_index())

print("\nRoom type counts:")
print(df["room_type"].value_counts(dropna=False))

print("\nNeighbourhood counts:")
print(df["neighbourhood"].value_counts(dropna=False).head(20))

# ------------------------------------------------------------
# 6. Save useful project-specific summaries
# ------------------------------------------------------------

# Listings by month
listings_by_month = df["month_year"].value_counts().sort_index().reset_index()
listings_by_month.columns = ["month_year", "listing_count"]
listings_by_month.to_csv(
    SUMMARY_TABLES / "listings_by_month.csv",
    index=False
)

# Room type counts
room_type_counts = df["room_type"].value_counts(dropna=False).reset_index()
room_type_counts.columns = ["room_type", "count"]
room_type_counts.to_csv(
    SUMMARY_TABLES / "room_type_counts.csv",
    index=False
)

# Neighbourhood counts
neighbourhood_counts = df["neighbourhood"].value_counts(dropna=False).reset_index()
neighbourhood_counts.columns = ["neighbourhood", "count"]
neighbourhood_counts.to_csv(
    SUMMARY_TABLES / "neighbourhood_counts.csv",
    index=False
)

print("\nSummary files saved to:")
print(SUMMARY_TABLES)