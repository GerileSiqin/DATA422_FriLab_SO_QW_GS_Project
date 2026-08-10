# 00_test_load_one_dataset.py
# Purpose:
# Test whether Python can load one Airbnb listings.csv file correctly.
# Then check basic information and filter Christchurch City only.

# ------------------------------------------------------------
# 1. Import libraries
# ------------------------------------------------------------

# pathlib is a Python standard library.
# Path helps us build file paths safely on Windows/Mac/Linux.
from pathlib import Path

# pandas is a data-analysis library.
# We use pandas to read CSV files and work with tables/dataframes.
import pandas as pd

# ------------------------------------------------------------
# 2. Define project folders
# ------------------------------------------------------------

# __file__ means the current Python script file.
# Path(__file__).resolve() gives the full path of this script.
# parents[2] moves two folders up to reach the project root folder.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# DATA_RAW is the folder where the downloaded raw Airbnb CSV files are stored.
# The / operator from pathlib joins folder names into a file path.
DATA_RAW = PROJECT_ROOT / "deliverable_3" / "data_raw"

# ------------------------------------------------------------
# 3. Choose one dataset to test
# ------------------------------------------------------------

# file_path points to one CSV file.
# We test one dataset first before processing all monthly datasets.
file_path = DATA_RAW / "listings_19062026.csv"

# ------------------------------------------------------------
# 4. Load the dataset
# ------------------------------------------------------------

# pd.read_csv() is a pandas function.
# It reads a CSV file and loads it into a pandas DataFrame called df.
# A DataFrame is like a table with rows and columns.
df = pd.read_csv(file_path)

# ------------------------------------------------------------
# 5. Show basic information
# ------------------------------------------------------------

# print() displays information in the terminal.
print("File loaded successfully.")
print("File path:", file_path)

# df.shape shows the size of the table.
# It returns: (number of rows, number of columns)
print("Rows and columns:", df.shape)

# df.columns.tolist() shows all column names as a list.
print("\nColumn names:")
print(df.columns.tolist())

# df.head() shows the first 5 rows of the dataset.
print("\nFirst 5 rows:")
print(df.head())

# value_counts() counts how many rows are in each neighbourhood_group.
# dropna=False means missing values are also counted if they exist.
print("\nNeighbourhood groups:")
print(df["neighbourhood_group"].value_counts(dropna=False))

# ------------------------------------------------------------
# 6. Filter Christchurch City only
# ------------------------------------------------------------

# This filters the DataFrame.
# It keeps only rows where neighbourhood_group equals "Christchurch City".
christchurch = df[df["neighbourhood_group"] == "Christchurch City"]

# ------------------------------------------------------------
# 7. Show Christchurch information
# ------------------------------------------------------------

# christchurch.shape shows the number of Christchurch rows and columns.
print("\nChristchurch rows and columns:")
print(christchurch.shape)

# christchurch.head() shows the first 5 Christchurch rows.
print("\nFirst 5 Christchurch rows:")
print(christchurch.head())

# value_counts() counts how many Christchurch listings are in each room type.
print("\nChristchurch room types:")
print(christchurch["room_type"].value_counts(dropna=False))