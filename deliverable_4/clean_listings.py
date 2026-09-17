"""
Inspect and begin cleaning the Christchurch listing dataset
for DATA422 Deliverable 4.

This script:
1. Sets the output folder for the cleaned dataset.
2. Sets the original CSV file.
3. Reads the dataset.
4. Inspects rows, columns, data types, and missing values.
5. Checks for exact duplicate rows.
6. Removes exact duplicate rows if any exist.
7. Checks latitude and longitude.
8. Investigates important columns before further cleaning.
9. Investigates unusually high price values.
10. Checks price percentiles.

Author: L3G3
Date: 16 September 2026
"""

import pandas as pd
from pathlib import Path
from input_path import ask_csv_path


# --------------------------------------------------
# 1. Set the output folder for the cleaned dataset
# --------------------------------------------------

data_folder = Path(__file__).resolve().parent / "data_processed"


# --------------------------------------------------
# 2. Set the original CSV file
# --------------------------------------------------

default_input_file = (
    Path(__file__).resolve().parents[1]
    / "deliverable_3"
    / "data_processed"
    / "christchurch_airbnb_cleaned.csv"
)
input_file = ask_csv_path(default_input_file, "Christchurch Airbnb")

print("Input file:")
print(input_file)


# --------------------------------------------------
# 3. Read the dataset
# --------------------------------------------------

df = pd.read_csv(input_file)

print("\n--- ORIGINAL DATASET ---")
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")


# --------------------------------------------------
# 4. Inspect the columns
# --------------------------------------------------

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())


# --------------------------------------------------
# 5. Inspect data types
# --------------------------------------------------

print("\n--- DATA TYPES ---")
print(df.dtypes)


# --------------------------------------------------
# 6. Check missing values
# --------------------------------------------------

print("\n--- MISSING VALUES ---")
print(df.isna().sum())


# --------------------------------------------------
# 7. Check duplicate rows
# --------------------------------------------------

duplicate_count = df.duplicated().sum()

print("\n--- DUPLICATES ---")
print(f"Number of duplicate rows: {duplicate_count}")


# --------------------------------------------------
# 8. Remove exact duplicate rows
# --------------------------------------------------

rows_before_duplicates = len(df)

df = df.drop_duplicates()

rows_after_duplicates = len(df)

duplicates_removed = rows_before_duplicates - rows_after_duplicates

print(f"Duplicate rows removed: {duplicates_removed}")


# --------------------------------------------------
# 9. Check latitude and longitude
# --------------------------------------------------

print("\n--- LATITUDE AND LONGITUDE ---")

print(f"Missing latitude values: {df['latitude'].isna().sum()}")
print(f"Missing longitude values: {df['longitude'].isna().sum()}")


# --------------------------------------------------
# 10. Investigate important columns
# --------------------------------------------------

print("\n--- PRICE SUMMARY ---")
print(df["price"].describe())

print("\n--- ROOM TYPES ---")
print(df["room_type"].value_counts(dropna=False))

print("\n--- NEIGHBOURHOOD GROUPS ---")
print(df["neighbourhood_group"].value_counts(dropna=False))

print("\n--- MONTHS IN DATASET ---")
print(df["month_year"].value_counts().sort_index())

print("\n--- MISSING PRICE BY MONTH ---")
print(
    df.groupby("month_year")["price"]
    .apply(lambda x: x.isna().sum())
)

print("\n--- MISSING PRICE BY ROOM TYPE ---")
print(
    df.groupby("room_type")["price"]
    .apply(lambda x: x.isna().sum())
)


# --------------------------------------------------
# 11. Investigate high price values
# --------------------------------------------------

print("\n--- HIGHEST PRICE VALUES ---")

print(
    df[
        [
            "id",
            "name",
            "neighbourhood",
            "room_type",
            "price",
            "minimum_nights",
            "month_year"
        ]
    ]
    .sort_values("price", ascending=False)
    .head(20)
)


# --------------------------------------------------
# 12. Check price percentiles
# --------------------------------------------------

print("\n--- PRICE PERCENTILES ---")

print(
    df["price"].quantile(
        [0.90, 0.95, 0.99, 0.995, 0.999]
    )
)


# --------------------------------------------------
# 13. Dataset after initial checks
# --------------------------------------------------

print("\n--- DATASET AFTER INITIAL CHECKS ---")

print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")


# --------------------------------------------------
# 14. Drop unnecessary columns
# --------------------------------------------------

columns_to_drop = [
    "name",
    "host_id",
    "host_name",
    "neighbourhood_group",
    "number_of_reviews",
    "last_review",
    "reviews_per_month",
    "number_of_reviews_ltm",
    "license"
]

df = df.drop(columns=columns_to_drop)

print("\n--- COLUMNS AFTER CLEANING ---")
print(df.columns.tolist())


# --------------------------------------------------
# 15. Keep missing price values
# --------------------------------------------------

# Missing price values are kept because December 2025,
# January 2026, and February 2026 have no price data.
# Removing these rows would remove entire months from
# the dataset and affect later availability analysis.

print("\n--- MISSING PRICE VALUES KEPT ---")
print(f"Missing price values: {df['price'].isna().sum()}")


# --------------------------------------------------
# 16. Keep missing minimum_nights values
# --------------------------------------------------

# Only 37 minimum_nights values are missing.
# These rows are kept because minimum_nights is not
# essential for the later rental price and availability comparison.

print("\n--- MISSING MINIMUM NIGHTS VALUES KEPT ---")
print(
    f"Missing minimum_nights values: "
    f"{df['minimum_nights'].isna().sum()}"
)


# --------------------------------------------------
# 17. Check final missing values
# --------------------------------------------------

print("\n--- FINAL MISSING VALUES ---")
print(df.isna().sum())


# --------------------------------------------------
# 18. Final dataset information
# --------------------------------------------------

print("\n--- FINAL CLEANED DATASET ---")
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")


# --------------------------------------------------
# 19. Save the cleaned dataset
# --------------------------------------------------

output_file = data_folder / "christchurch_listings_clean.csv"

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

print("\nCleaned dataset saved as:")
print(output_file)
