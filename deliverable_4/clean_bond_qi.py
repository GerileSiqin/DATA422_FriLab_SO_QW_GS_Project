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
7. Keeps the three selected quarters and removes missing and -99 Location Id rows.
8. Saves a separate bond_data_clean_qi.csv output.
9. Generates a Markdown report of all inspection and cleaning activities.

Author: L3G3
Date: 17 September 2026
"""

import pandas as pd
from pathlib import Path
from input_path import ask_csv_path
from datetime import datetime


def generate_cleaning_report(original, cleaned, stages, input_file, output_file,
                             report_file, target_timeframes):
    """Save a readable activity report using the results of this cleaning run."""
    def table(headers, rows):
        def cell(value):
            return str(value).replace("|", "\\|").replace("\n", " ")
        return "\n".join([
            "| " + " | ".join(map(cell, headers)) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
            *["| " + " | ".join(map(cell, row)) + " |" for row in rows],
        ])

    activity_rows = []
    previous_rows = len(original)
    for activity, remaining in stages:
        activity_rows.append([activity, previous_rows, previous_rows - remaining,
                              remaining])
        previous_rows = remaining

    missing_rows = [
        [column, int(original[column].isna().sum()),
         int(cleaned[column].isna().sum())]
        for column in original.columns
    ]
    quarter_rows = [
        [quarter, int(original["TimeFrame"].eq(quarter).sum()),
         int(cleaned["TimeFrame"].eq(quarter).sum())]
        for quarter in target_timeframes
    ]
    checks = [
        ["No missing Location Id", not cleaned["Location Id"].isna().any()],
        ["No Location Id equal to -99", not cleaned["Location Id"].eq(-99).any()],
        ["Only selected quarters", cleaned["TimeFrame"].isin(target_timeframes).all()],
        ["All original columns retained", list(original.columns) == list(cleaned.columns)],
        ["Row counts reconcile", sum(row[2] for row in activity_rows)
         + len(cleaned) == len(original)],
    ]
    sections = [
        "# Rental bond data cleaning report — Qi",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "## Files and scope",
        f"Input: `{input_file}`\n\nCleaned CSV: `{output_file}`",
        "Selected quarterly dates: " + ", ".join(target_timeframes) + ".",
        "Counts refer to dataset rows, not individual bonds or tenancies. "
        "No Christchurch geographic selection or Airbnb merge is performed. "
        "The raw input is not modified.",
        "## Outcome",
        f"Input: **{len(original):,} rows × {len(original.columns)} columns**. "
        f"Output: **{len(cleaned):,} rows × {len(cleaned.columns)} columns**. "
        f"Total rows removed: **{len(original) - len(cleaned):,}**.",
        "## Inspection activities",
        "The script inspects dimensions, column names, data types, sample records, "
        "missing values, exact duplicates, required fields, timeframe counts, location "
        "IDs, unique values, dwelling types and bedroom categories. It also examines "
        "missing bedrooms by dwelling type and samples records with missing location "
        "IDs or median rent. These inspections do not themselves change values.",
        table(["Column", "Input type", "Output type", "Input unique values (including missing)"],
              [[c, original[c].dtype, cleaned[c].dtype,
                original[c].nunique(dropna=False)] for c in original.columns]),
        "## Cleaning activities in execution order",
        table(["Activity", "Rows before", "Rows removed", "Rows remaining"], activity_rows),
        "Rows outside the selected quarters are excluded first. Missing location IDs "
        "are then excluded because they cannot support geographic matching. The special "
        "location code -99 is excluded for the same analysis purpose; its exact meaning "
        "is not assumed. Removal counts are sequential and do not double-count rows.",
        "## Decisions to retain data",
        "All columns are retained. No missing values are filled, no rent outliers are "
        "removed, and no rent values are converted. Missing bedroom values and any "
        "remaining missing rent values are retained. There is no duplicate-removal "
        "step; duplicates are checked and reported only.",
        f"Exact duplicates in input: **{int(original.duplicated().sum()):,}**. "
        f"Exact duplicates in output: **{int(cleaned.duplicated().sum()):,}**.",
        "## Missing values before and after cleaning",
        "The input counts cover all periods; the output counts cover the retained "
        "quarters and locations. A reduction does not indicate imputation.",
        table(["Column", "Input missing", "Output missing"], missing_rows),
        "## Retained quarterly coverage",
        table(["TimeFrame", "Input rows in quarter", "Output rows in quarter"], quarter_rows),
        "## Validation",
        table(["Check", "Result"], [[label, "PASS" if passed else "FAIL"]
                                     for label, passed in checks]),
        "An empty output cannot support analysis." if cleaned.empty else
        "The output contains records. Passing these checks confirms the stated filters; "
        "it does not establish that every retained location is in Christchurch.",
        "## Reproduction",
        "Run `clean_bond_qi.py` and select the input CSV when prompted. "
        "The script regenerates `bond_data_clean_qi.csv` and this report in "
        "`bond_data_processed/` using the selected input and current filtering rules.",
    ]
    report_file = Path(report_file)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    return report_file


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
original_df = df.copy()
cleaning_stages = []

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
cleaning_stages.append(("Keep selected quarterly dates", len(df)))

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
cleaning_stages.append(("Remove missing Location Id", len(df)))

print("\n--- MISSING LOCATION ID HANDLING ---")
print(
    f"Rows removed because Location Id was missing: "
    f"{rows_before_location_filter - rows_after_location_filter}"
)


# --------------------------------------------------
# 22b. Remove rows with Location Id equal to -99
# --------------------------------------------------

# Exclude this special location code from geographic matching.
# Keep the raw data unchanged; its exact code meaning is not assumed here.
rows_before_minus99_filter = len(df)

df = df.loc[df["Location Id"] != -99].copy()
cleaning_stages.append(("Remove Location Id equal to -99", len(df)))

print("\n--- SPECIAL LOCATION ID HANDLING ---")
print(
    f"Rows removed because Location Id was -99: "
    f"{rows_before_minus99_filter - len(df)}"
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

output_file = processed_data_folder / "bond_data_clean_qi.csv"

df.to_csv(output_file, index=False)

print("\nCleaned bond dataset saved as:")
print(output_file)


# --------------------------------------------------
# 27. Generate the cleaning activity report
# --------------------------------------------------

report_file = generate_cleaning_report(
    original_df, df, cleaning_stages, input_file, output_file,
    processed_data_folder / "bond_data_cleaning_report_qi.md",
    target_timeframes,
)

print("\nCleaning activity report saved as:")
print(report_file)
