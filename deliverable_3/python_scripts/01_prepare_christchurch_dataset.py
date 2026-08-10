# 01_prepare_christchurch_dataset.py
# Purpose:
# Load all monthly New Zealand Airbnb listings.csv files,
# filter Christchurch City only,
# add a month_year column,
# concatenate all monthly Christchurch datasets,
# and save the final combined dataset.

# ------------------------------------------------------------
# 1. Import libraries
# ------------------------------------------------------------

# pathlib is a Python standard library.
# Path helps create file paths safely.
from pathlib import Path

# pandas is used for reading CSV files, filtering data,
# adding columns, and combining datasets.
import pandas as pd

# ------------------------------------------------------------
# 2. Define project folders
# ------------------------------------------------------------

# __file__ means the current Python script file.
# resolve() gets the full path.
# parents[2] moves up two folders to the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# DATA_RAW stores the original monthly downloaded CSV files.
DATA_RAW = PROJECT_ROOT / "deliverable_3" / "data_raw"

# DATA_PROCESSED stores the final processed dataset.
DATA_PROCESSED = PROJECT_ROOT / "deliverable_3" / "data_processed"

# ------------------------------------------------------------
# 3. Make sure processed data folder exists
# ------------------------------------------------------------

# mkdir() creates a folder.
# parents=True means create parent folders if needed.
# exist_ok=True means do not show an error if the folder already exists.
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# 4. List monthly datasets
# ------------------------------------------------------------

# files is a list of tuples.
# Each tuple has two parts:
# 1. month_year = the month label we want to add to the data
# 2. file_name = the actual CSV file name in data_raw
files = [
    ("2025-10", "listings_05102025.csv"),
    ("2025-11", "listings_07112025.csv"),
    ("2025-12", "listings_11122025.csv"),
    ("2026-01", "listings_16012026.csv"),
    ("2026-02", "listings_13022026.csv"),
    ("2026-03", "listings_17032026.csv"),
    ("2026-04", "listings_16042026.csv"),
    ("2026-05", "listings_23052026.csv"),
    ("2026-06", "listings_19062026.csv"),
]

# ------------------------------------------------------------
# 5. Create an empty list for filtered Christchurch data
# ------------------------------------------------------------

# This empty list will store each month's Christchurch-only dataset.
# Later, pandas will concatenate everything in this list.
all_christchurch_data = []

# ------------------------------------------------------------
# 6. Loop through each monthly file
# ------------------------------------------------------------

# This for loop goes through each tuple in the files list.
# month_year gets the month label, such as "2025-10".
# file_name gets the CSV filename, such as "listings_05102025.csv".
for month_year, file_name in files:
    # Build the full path to the CSV file.
    file_path = DATA_RAW / file_name

    # Print which file is currently being loaded.
    print(f"Loading {file_name}...")

    # ------------------------------------------------------------
    # 7. Load one monthly New Zealand dataset
    # ------------------------------------------------------------

    # pd.read_csv() reads the CSV file into a pandas DataFrame called df.
    df = pd.read_csv(file_path)

    # ------------------------------------------------------------
    # 8. Filter Christchurch City only
    # ------------------------------------------------------------

    # This keeps only rows where neighbourhood_group is Christchurch City.
    # .copy() creates a separate copy, so we can safely add a new column later.
    chch = df[df["neighbourhood_group"] == "Christchurch City"].copy()

    # ------------------------------------------------------------
    # 9. Add month_year column
    # ------------------------------------------------------------

    # This adds a new column to record which month this data came from.
    # This is important after all months are combined.
    chch["month_year"] = month_year

    # Print how many Christchurch listings were found for this month.
    print(f"{month_year}: {len(chch)} Christchurch listings")

    # ------------------------------------------------------------
    # 10. Add this month's Christchurch data to the list
    # ------------------------------------------------------------

    # append() adds the filtered monthly DataFrame into the list.
    all_christchurch_data.append(chch)

# ------------------------------------------------------------
# 11. Concatenate all monthly Christchurch datasets
# ------------------------------------------------------------

# pd.concat() combines all monthly Christchurch DataFrames into one big DataFrame.
# ignore_index=True resets the row index from 0 to the final row number.
combined = pd.concat(all_christchurch_data, ignore_index=True)

# ------------------------------------------------------------
# 12. Print summary information
# ------------------------------------------------------------

# Show the final size of the combined Christchurch dataset.
print("\nCombined Christchurch dataset:")
print("Rows and columns:", combined.shape)

# Count how many listings there are in each month.
# value_counts() counts rows by month_year.
# sort_index() sorts months in chronological order.
print("\nListings by month:")
print(combined["month_year"].value_counts().sort_index())

# ------------------------------------------------------------
# 13. Save combined Christchurch dataset
# ------------------------------------------------------------

# Define the output file path.
output_file = DATA_PROCESSED / "christchurch_airbnb_oct2025_jun2026.csv"

# to_csv() saves the combined DataFrame as a CSV file.
# index=False means do not save the pandas row index as an extra column.
combined.to_csv(output_file, index=False)

# Print where the final file was saved.
print("\nSaved combined dataset to:")
print(output_file)