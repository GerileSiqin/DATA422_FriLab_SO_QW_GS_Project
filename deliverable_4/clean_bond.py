"""
Inspect and begin cleaning the rental bond dataset
for DATA422 Deliverable 4.

This script:
1. Sets the folders and input CSV file.
2. Reads the rental bond dataset.
3. Inspects rows, columns, data types, and sample records.
4. Checks missing values and duplicate rows.
5. Checks the required Location Id and TimeFrame columns.
6. Investigates the timeframe and location fields before further cleaning.

Author: L3G3
Date: 17 September 2026
"""

import pandas as pd
from pathlib import Path
from input_path import ask_csv_path


# --------------------------------------------------
# 1. Set the folders
# --------------------------------------------------

project_folder = Path(__file__).resolve().parent

raw_data_folder = project_folder / "bond_data_raw"


# --------------------------------------------------
# 2. Set the original CSV file
# --------------------------------------------------

input_file = ask_csv_path(
    raw_data_folder / "Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv",
    "rental bond",
)

print("Input file:")
print(input_file)


# --------------------------------------------------
# 3. Read the dataset
# --------------------------------------------------

df = pd.read_csv(input_file)

print("\n--- ORIGINAL BOND DATASET ---")
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")


# --------------------------------------------------
# 4. Inspect the column names
# --------------------------------------------------

print("\n--- COLUMN NAMES ---")

for column in df.columns:
    print(column)


# --------------------------------------------------
# 5. Inspect data types
# --------------------------------------------------

print("\n--- DATA TYPES ---")
print(df.dtypes)


# --------------------------------------------------
# 6. View sample records
# --------------------------------------------------

print("\n--- FIRST 5 ROWS ---")
print(df.head())


# --------------------------------------------------
# 7. Check missing values
# --------------------------------------------------

print("\n--- MISSING VALUES ---")
print(df.isna().sum())


# --------------------------------------------------
# 8. Check duplicate rows
# --------------------------------------------------

duplicate_count = df.duplicated().sum()

print("\n--- DUPLICATES ---")
print(f"Number of exact duplicate rows: {duplicate_count}")


# --------------------------------------------------
# 9. Check required columns
# --------------------------------------------------

print("\n--- REQUIRED COLUMNS ---")

required_columns = ["Location Id", "TimeFrame"]

for column in required_columns:
    if column in df.columns:
        print(f"{column}: found")
    else:
        print(f"{column}: NOT FOUND")


# --------------------------------------------------
# 10. Check missing values in required columns
# --------------------------------------------------

print("\n--- MISSING VALUES IN REQUIRED COLUMNS ---")

for column in required_columns:
    if column in df.columns:
        print(f"{column}: {df[column].isna().sum()}")


# --------------------------------------------------
# 11. Investigate TimeFrame
# --------------------------------------------------

print("\n--- TIMEFRAME VALUES ---")

if "TimeFrame" in df.columns:
    print(df["TimeFrame"].value_counts(dropna=False).sort_index())


# --------------------------------------------------
# 12. Investigate Location Id
# --------------------------------------------------

print("\n--- LOCATION ID ---")

if "Location Id" in df.columns:
    print(f"Number of unique Location Id values: "
          f"{df['Location Id'].nunique()}")

    print("\nSample Location Id values:")
    print(df["Location Id"].drop_duplicates().head(20))


# --------------------------------------------------
# 13. Check unique values in each column
# --------------------------------------------------

print("\n--- NUMBER OF UNIQUE VALUES BY COLUMN ---")

for column in df.columns:
    print(f"{column}: {df[column].nunique(dropna=False)}")


# --------------------------------------------------
# 14. Dataset after initial checks
# --------------------------------------------------

print("\n--- DATASET AFTER INITIAL CHECKS ---")
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")


# --------------------------------------------------
# 15. Investigate dwelling types
# --------------------------------------------------

print("\n--- DWELLING TYPES ---")
print(df["Dwelling Type"].value_counts(dropna=False))


# --------------------------------------------------
# 16. Investigate number of beds
# --------------------------------------------------

print("\n--- NUMBER OF BEDS ---")
print(df["Number Of Beds"].value_counts(dropna=False))


# --------------------------------------------------
# 17. Check missing beds by dwelling type
# --------------------------------------------------

print("\n--- MISSING NUMBER OF BEDS BY DWELLING TYPE ---")

print(
    df.groupby("Dwelling Type")["Number Of Beds"]
    .apply(lambda x: x.isna().sum())
)


# --------------------------------------------------
# 18. Check rows with missing Location Id
# --------------------------------------------------

print("\n--- ROWS WITH MISSING LOCATION ID ---")

print(
    df[df["Location Id"].isna()]
    .head(20)
)


# --------------------------------------------------
# 19. Check rows with missing rent values
# --------------------------------------------------

print("\n--- ROWS WITH MISSING MEDIAN RENT ---")

print(
    df[df["Median Rent"].isna()]
    .head(20)
)


# --------------------------------------------------
# 20. Check target timeframes
# --------------------------------------------------

target_timeframes = [
    "2025-10-01",
    "2026-01-01",
    "2026-04-01"
]

target_df = df[df["TimeFrame"].isin(target_timeframes)]

print("\n--- TARGET TIMEFRAME SUMMARY ---")
print(target_df["TimeFrame"].value_counts().sort_index())

print(f"\nRows in target period: {len(target_df)}")


# --------------------------------------------------
# 21. Filter to the target timeframes
# --------------------------------------------------

target_timeframes = [
    "2025-10-01",
    "2026-01-01",
    "2026-04-01"
]

rows_before_time_filter = len(df)

df = df[df["TimeFrame"].isin(target_timeframes)].copy()

rows_after_time_filter = len(df)

print("\n--- TIMEFRAME FILTERING ---")
print(f"Rows before filtering: {rows_before_time_filter}")
print(f"Rows after filtering: {rows_after_time_filter}")
print(
    f"Rows removed outside target period: "
    f"{rows_before_time_filter - rows_after_time_filter}"
)


# --------------------------------------------------
# 22. Remove rows with missing Location Id
# --------------------------------------------------

rows_before_location_filter = len(df)

df = df.dropna(subset=["Location Id"])

rows_after_location_filter = len(df)

print("\n--- MISSING LOCATION ID HANDLING ---")
print(
    f"Rows removed because Location Id was missing: "
    f"{rows_before_location_filter - rows_after_location_filter}"
)


# --------------------------------------------------
# 23. Keep missing Number Of Beds values
# --------------------------------------------------

print("\n--- MISSING NUMBER OF BEDS VALUES KEPT ---")
print(
    f"Missing Number Of Beds values remaining: "
    f"{df['Number Of Beds'].isna().sum()}"
)


# --------------------------------------------------
# 24. Check remaining missing values
# --------------------------------------------------

print("\n--- MISSING VALUES AFTER CLEANING ---")
print(df.isna().sum())


# --------------------------------------------------
# 25. Final cleaned dataset information
# --------------------------------------------------

print("\n--- FINAL CLEANED BOND DATASET ---")
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")


# --------------------------------------------------
# 26. Save the cleaned dataset
# --------------------------------------------------

processed_data_folder = project_folder / "bond_data_processed"

processed_data_folder.mkdir(exist_ok=True)

output_file = processed_data_folder / "bond_data_clean.csv"

df.to_csv(output_file, index=False)

print("\nCleaned bond dataset saved as:")
print(output_file)
