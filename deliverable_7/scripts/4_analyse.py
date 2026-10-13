"""
Run Deliverable 7 analyses.

This script:
1. Calculates median Airbnb price by month for:
   - Christchurch overall
   - Christchurch Central
2. Joins Airbnb and Bond data.
3. Calculates long-term daily rent and rental gap.
4. Calculates median rental gap by month.
5. Saves all analysis outputs.

Author: Gerile
"""

import pandas as pd


# -----------------------------------
# File paths
# -----------------------------------

AIRBNB_FILE = "output/3_airbnb_ready_for_join.csv"
BOND_FILE = "input/bond_data_clean.csv"

AIRBNB_PRICE_OUTPUT = "output/4_airbnb_price_by_time.csv"
JOINED_OUTPUT = "output/4_airbnb_bond_joined.csv"
RENTAL_GAP_OUTPUT = "output/4_rental_gap_by_time.csv"


# -----------------------------------
# Christchurch Central location ID
# -----------------------------------

CHRISTCHURCH_CENTRAL_ID = 326600


# -----------------------------------
# Read data
# -----------------------------------

print("\n===================================")
print("Running Deliverable 7 analyses")
print("===================================")

airbnb = pd.read_csv(AIRBNB_FILE)
bond = pd.read_csv(BOND_FILE)

print("\nAirbnb rows:")
print(len(airbnb))

print("\nBond rows:")
print(len(bond))


# -----------------------------------
# Check required columns
# -----------------------------------

required_airbnb_columns = [
    "id",
    "location_id",
    "location_name",
    "month_year",
    "TimeFrame",
    "price"
]

required_bond_columns = [
    "Location Id",
    "TimeFrame",
    "Median Rent",
    "Dwelling Type",
    "Number Of Beds"
]


for column in required_airbnb_columns:

    if column not in airbnb.columns:
        raise ValueError(
            f"Missing Airbnb column: {column}"
        )


for column in required_bond_columns:

    if column not in bond.columns:
        raise ValueError(
            f"Missing Bond column: {column}"
        )


# -----------------------------------
# Prepare data types
# -----------------------------------

airbnb["month_year"] = pd.to_datetime(
    airbnb["month_year"]
)

airbnb["TimeFrame"] = pd.to_datetime(
    airbnb["TimeFrame"]
)

bond["TimeFrame"] = pd.to_datetime(
    bond["TimeFrame"]
)


airbnb["location_id"] = pd.to_numeric(
    airbnb["location_id"],
    errors="coerce"
).astype("Int64")


bond["Location Id"] = pd.to_numeric(
    bond["Location Id"],
    errors="coerce"
).astype("Int64")


# ===================================
# Analysis 1:
# Airbnb median price by month
# ===================================

print("\n===================================")
print("Analysis 1: Airbnb median prices")
print("===================================")


# -----------------------------------
# Christchurch overall
# -----------------------------------

overall_price = (
    airbnb
    .groupby("month_year")
    .agg(
        christchurch_median_price=(
            "price",
            "median"
        )
    )
    .reset_index()
)


# -----------------------------------
# Christchurch Central
# -----------------------------------

central = airbnb[
    airbnb["location_id"]
    == CHRISTCHURCH_CENTRAL_ID
].copy()


print("\nChristchurch Central rows:")
print(len(central))


if len(central) == 0:
    raise ValueError(
        "No Christchurch Central Airbnb rows found."
    )


central_price = (
    central
    .groupby("month_year")
    .agg(
        central_median_price=(
            "price",
            "median"
        )
    )
    .reset_index()
)


# -----------------------------------
# Combine price summaries
# -----------------------------------

airbnb_price_by_time = overall_price.merge(
    central_price,
    on="month_year",
    how="left"
)

airbnb_price_by_time = (
    airbnb_price_by_time
    .sort_values("month_year")
)


print("\nAirbnb median price by month:")
print(airbnb_price_by_time)


# -----------------------------------
# Save Airbnb price analysis
# -----------------------------------

airbnb_price_by_time.to_csv(
    AIRBNB_PRICE_OUTPUT,
    index=False
)

print("\nSaved:")
print(AIRBNB_PRICE_OUTPUT)


# ===================================
# Analysis 2:
# Airbnb-Bond rental gap
# ===================================

print("\n===================================")
print("Analysis 2: Airbnb-Bond rental gap")
print("===================================")


# -----------------------------------
# Filter Bond data
# -----------------------------------

bond_summary = bond[
    (bond["Dwelling Type"] == "ALL")
    &
    (bond["Number Of Beds"] == "ALL")
].copy()


print("\nBond rows after filtering:")
print(len(bond_summary))


# -----------------------------------
# Check duplicate Bond join keys
# -----------------------------------

bond_key_counts = (
    bond_summary
    .groupby(
        [
            "Location Id",
            "TimeFrame"
        ]
    )
    .size()
)


duplicate_bond_keys = bond_key_counts[
    bond_key_counts > 1
]


print(
    "\nDuplicate Bond "
    "Location Id + TimeFrame combinations:"
)

print(len(duplicate_bond_keys))


if len(duplicate_bond_keys) > 0:

    raise ValueError(
        "Duplicate Bond join keys found."
    )


# -----------------------------------
# Join Airbnb and Bond
# -----------------------------------

joined = airbnb.merge(
    bond_summary,
    left_on=[
        "location_id",
        "TimeFrame"
    ],
    right_on=[
        "Location Id",
        "TimeFrame"
    ],
    how="inner"
)


print("\nRows after inner join:")
print(len(joined))


if len(joined) == 0:
    raise ValueError(
        "The Airbnb-Bond join returned no rows."
    )


# -----------------------------------
# Show included months
# -----------------------------------

included_months = (
    joined["month_year"]
    .drop_duplicates()
    .sort_values()
)

print("\nAirbnb months included after join:")
print(included_months)


# -----------------------------------
# Show included Bond quarters
# -----------------------------------

included_quarters = (
    joined["TimeFrame"]
    .drop_duplicates()
    .sort_values()
)

print("\nBond quarters included after join:")
print(included_quarters)


# -----------------------------------
# Remove unusable rows
# -----------------------------------

rows_before = len(joined)

joined = joined.dropna(
    subset=[
        "price",
        "Median Rent"
    ]
)

rows_removed = (
    rows_before
    - len(joined)
)


print(
    "\nRows removed because price "
    "or Median Rent was missing:"
)

print(rows_removed)


# -----------------------------------
# Calculate long-term daily rent
# -----------------------------------

joined["long_term_daily_rent"] = (
    joined["Median Rent"] / 7
)


# -----------------------------------
# Calculate rental gap
# -----------------------------------

joined["rental_gap"] = (
    joined["price"]
    - joined["long_term_daily_rent"]
)


# -----------------------------------
# Show example calculations
# -----------------------------------

example_columns = [
    "location_name",
    "month_year",
    "TimeFrame",
    "price",
    "Median Rent",
    "long_term_daily_rent",
    "rental_gap"
]


print("\nExample rental-gap calculations:")

print(
    joined[
        example_columns
    ].head(10)
)


# -----------------------------------
# Summarise rental gap by month
# -----------------------------------

rental_gap_by_time = (
    joined
    .groupby("month_year")
    .agg(
        airbnb_records=(
            "id",
            "count"
        ),

        median_airbnb_price=(
            "price",
            "median"
        ),

        median_long_term_daily_rent=(
            "long_term_daily_rent",
            "median"
        ),

        median_rental_gap=(
            "rental_gap",
            "median"
        )
    )
    .reset_index()
    .sort_values("month_year")
)


print("\nRental gap by month:")
print(rental_gap_by_time)


# -----------------------------------
# Save rental-gap outputs
# -----------------------------------

joined.to_csv(
    JOINED_OUTPUT,
    index=False
)

rental_gap_by_time.to_csv(
    RENTAL_GAP_OUTPUT,
    index=False
)


print("\nSaved:")
print(JOINED_OUTPUT)
print(RENTAL_GAP_OUTPUT)


# -----------------------------------
# Complete
# -----------------------------------

print("\n===================================")
print("Analysis completed successfully")
print("===================================")