"""
Inspect and begin cleaning the Christchurch listing dataset
for DATA422 Deliverable 4.

This script:
1. Sets the output folder for the cleaned dataset.
2. Asks for the source CSV path (Enter uses the Deliverable 3 cleaned CSV).
3. Reads the dataset.
4. Inspects rows, columns, data types, and missing values.
5. Checks for exact duplicate rows.
6. Removes exact duplicate rows if any exist.
7. Checks latitude and longitude.
8. Investigates important columns before further cleaning.
9. Investigates unusually high price values.
10. Checks price percentiles.
11. Retains name, host_id, and host_name.
12. Saves a separate christchurch_listings_clean_qi.csv output.
13. Generates a Markdown report covering all inspection and cleaning activities.

Author: L3G3
Date: 16 September 2026
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from input_path import ask_csv_path


def generate_cleaning_report(
    original,
    cleaned,
    input_file,
    output_file,
    report_file,
    columns_removed,
    duplicates_removed,
):
    """Create a Markdown summary of the completed cleaning activities."""

    def markdown_table(headers, rows):
        def format_cell(value):
            return str(value).replace("|", "\\|").replace("\n", " ")

        lines = [
            "| " + " | ".join(map(format_cell, headers)) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        lines.extend(
            "| " + " | ".join(map(format_cell, row)) + " |" for row in rows
        )
        return "\n".join(lines)

    missing_rows = [
        [
            column,
            int(original[column].isna().sum()),
            int(cleaned[column].isna().sum()) if column in cleaned.columns else "Removed",
        ]
        for column in original.columns
    ]
    month_rows = (
        [[month, int(count)] for month, count in
         cleaned["month_year"].value_counts(dropna=False).sort_index().items()]
        if "month_year" in cleaned.columns else []
    )
    checks = [
        ["All requested columns removed",
         all(column not in cleaned.columns for column in columns_removed)],
        ["name retained", "name" in cleaned.columns],
        ["host_id retained", "host_id" in cleaned.columns],
        ["host_name retained", "host_name" in cleaned.columns],
        ["No exact duplicate rows", not cleaned.duplicated().any()],
        ["Latitude has no missing values",
         "latitude" in cleaned.columns and not cleaned["latitude"].isna().any()],
        ["Longitude has no missing values",
         "longitude" in cleaned.columns and not cleaned["longitude"].isna().any()],
    ]

    sections = [
        "# Christchurch Airbnb cleaning report — Qi",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "## Files and scope",
        f"Input: `{input_file}`\n\nCleaned CSV: `{output_file}`",
        "The raw input file was read only and was not modified.",
        "## Outcome",
        f"Input: **{len(original):,} rows × {len(original.columns)} columns**. "
        f"Output: **{len(cleaned):,} rows × {len(cleaned.columns)} columns**. "
        f"Exact duplicate rows removed: **{duplicates_removed:,}**. "
        f"Columns removed: **{len(columns_removed)}**.",
        "## Inspection activities",
        "The script inspected the dataset dimensions, column names, data types, "
        "missing values, exact duplicates, latitude and longitude, price statistics, "
        "room types, neighbourhood groups, monthly coverage, missing-price patterns, "
        "the highest prices and selected price percentiles.",
        markdown_table(
            ["Column", "Input type", "Output type"],
            [[column, original[column].dtype,
              cleaned[column].dtype if column in cleaned.columns else "Removed"]
             for column in original.columns],
        ),
        "## Cleaning activities",
        f"Exact duplicate rows were checked and removed: **{duplicates_removed:,}**. "
        "No additional rows were removed. Missing prices and missing minimum-night "
        "values were retained, and high prices were inspected without applying an "
        "outlier-removal rule.",
        "The following columns were removed because they are outside the retained "
        "listing, host, location, price and availability fields:\n\n" +
        "\n".join(f"- `{column}`" for column in columns_removed),
        "The identifying fields `name`, `host_id` and `host_name` were retained as requested.",
        "## Final columns",
        "\n".join(f"- `{column}`" for column in cleaned.columns),
        "## Missing values before and after cleaning",
        "Missing values were not filled. ‘Removed’ means that the entire column was "
        "excluded from the output.",
        markdown_table(["Column", "Input missing", "Output missing"], missing_rows),
        "## Retained monthly coverage",
        markdown_table(["month_year", "Rows"], month_rows)
        if month_rows else "No `month_year` field is present in the output.",
        "## Validation",
        markdown_table(
            ["Check", "Result"],
            [[label, "PASS" if passed else "FAIL"] for label, passed in checks],
        ),
        "## Reproduction",
        "Run `clean_listing_qi.py`, then enter a CSV file path, a folder containing "
        "the expected CSV, or press Enter to use the displayed default. The script "
        "regenerates the cleaned CSV and this report in `data_processed/`.",
    ]

    report_file = Path(report_file)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    return report_file


# --------------------------------------------------
# 1. Set the output folder for the cleaned dataset
# --------------------------------------------------

data_folder = Path(__file__).resolve().parent / "data_processed"


# --------------------------------------------------
# 2. Locate the source CSV using the input prompt
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
original_df = df.copy()

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

# Keep name, host_id, and host_name for listing and host identification.
columns_to_drop = [
    "neighbourhood_group",
    "number_of_reviews",
    "last_review",
    "reviews_per_month",
    "number_of_reviews_ltm",
    "license",
    "source_file",
    "snapshot_date",
    "last_review_after_snapshot",
    "days_since_last_review"
]

df = df.drop(columns=columns_to_drop)

print("\n--- COLUMNS AFTER CLEANING ---")
print(df.columns.tolist())


# --------------------------------------------------
# 15. Keep missing price values
# --------------------------------------------------

# Keep rows with missing prices for later availability analysis.
# Missing counts and monthly patterns depend on the selected input file.

print("\n--- MISSING PRICE VALUES KEPT ---")
print(f"Missing price values: {df['price'].isna().sum()}")


# --------------------------------------------------
# 16. Keep missing minimum_nights values
# --------------------------------------------------

# Rows with missing minimum_nights are kept because this field is not
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

output_file = data_folder / "christchurch_listings_clean_qi.csv"

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

print("\nCleaned dataset saved as:")
print(output_file)


# --------------------------------------------------
# 20. Generate the final cleaning activity report
# --------------------------------------------------

report_file = generate_cleaning_report(
    original_df,
    df,
    input_file,
    output_file,
    data_folder / "christchurch_listings_cleaning_report_qi.md",
    columns_to_drop,
    duplicates_removed,
)

print("\nCleaning activity report saved as:")
print(report_file)
