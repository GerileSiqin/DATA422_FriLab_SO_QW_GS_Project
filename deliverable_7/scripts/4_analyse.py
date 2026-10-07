import pandas as pd


# File paths
AIRBNB_FILE = "output/3_airbnb_ready_for_join.csv"
BOND_FILE = "input/bond_data_clean.csv"

JOINED_OUTPUT = "output/4_airbnb_bond_joined.csv"
ANALYSIS_OUTPUT = "output/4_rental_gap_by_time.csv"


# -----------------------------------
# 1. Read datasets
# -----------------------------------

airbnb = pd.read_csv(
    AIRBNB_FILE
)

bond = pd.read_csv(
    BOND_FILE
)


print("\n-----------------------------------")
print("Airbnb and Bond analysis")
print("-----------------------------------")

print("\nAirbnb rows:")
print(len(airbnb))

print("\nBond rows:")
print(len(bond))


# -----------------------------------
# 2. Check required Airbnb columns
# -----------------------------------

required_airbnb_columns = [
    "id",
    "location_id",
    "location_name",
    "month_year",
    "TimeFrame",
    "price"
]

for column in required_airbnb_columns:

    if column not in airbnb.columns:

        raise ValueError(
            "Missing Airbnb column: " + column
        )


# -----------------------------------
# 3. Check required Bond columns
# -----------------------------------

required_bond_columns = [
    "Location Id",
    "TimeFrame",
    "Median Rent",
    "Dwelling Type",
    "Number Of Beds"
]

for column in required_bond_columns:

    if column not in bond.columns:

        raise ValueError(
            "Missing Bond column: " + column
        )


# -----------------------------------
# 4. Prepare date columns
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


# -----------------------------------
# 5. Prepare location ID columns
# -----------------------------------

airbnb["location_id"] = (
    airbnb["location_id"]
    .astype("Int64")
)

bond["Location Id"] = (
    bond["Location Id"]
    .astype("Int64")
)


# -----------------------------------
# 6. Filter Bond to overall rent
# -----------------------------------

bond_summary = bond[
    (bond["Dwelling Type"] == "ALL")
    &
    (bond["Number Of Beds"] == "ALL")
].copy()


print("\nBond rows after filtering:")
print(len(bond_summary))


# -----------------------------------
# 7. Check Bond join keys
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

duplicate_bond_keys = (
    bond_key_counts[
        bond_key_counts > 1
    ]
)


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
# 8. Join Airbnb and Bond
# -----------------------------------

joined = pd.merge(
    airbnb,
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


# -----------------------------------
# 9. Check months included after join
# -----------------------------------

print("\nAirbnb months included after join:")

print(
    joined["month_year"]
    .drop_duplicates()
    .sort_values()
)


# -----------------------------------
# 10. Check quarters included after join
# -----------------------------------

print("\nBond quarters included after join:")

print(
    joined["TimeFrame"]
    .drop_duplicates()
    .sort_values()
)


# -----------------------------------
# 11. Keep rows with usable prices
# -----------------------------------

before = len(joined)

analysis_data = joined[
    joined["price"].notna()
    &
    joined["Median Rent"].notna()
].copy()

after = len(analysis_data)


print(
    "\nRows removed because price "
    "or Median Rent was missing:"
)

print(before - after)


# -----------------------------------
# 12. Convert weekly rent to daily
# -----------------------------------

analysis_data[
    "long_term_daily_rent"
] = (
    analysis_data["Median Rent"] / 7
)


# -----------------------------------
# 13. Calculate rental gap
# -----------------------------------

analysis_data["rental_gap"] = (
    analysis_data["price"]
    -
    analysis_data["long_term_daily_rent"]
)


# -----------------------------------
# 14. Show example calculations
# -----------------------------------

print("\nExample rental-gap calculations:")

print(
    analysis_data[
        [
            "location_name",
            "month_year",
            "TimeFrame",
            "price",
            "Median Rent",
            "long_term_daily_rent",
            "rental_gap"
        ]
    ].head(10)
)


# -----------------------------------
# 15. Calculate median gap by month
# -----------------------------------

gap_by_time = (
    analysis_data
    .groupby(
        "month_year",
        as_index=False
    )
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
)


# -----------------------------------
# 16. Sort by month
# -----------------------------------

gap_by_time = (
    gap_by_time
    .sort_values(
        "month_year"
    )
    .reset_index(
        drop=True
    )
)


# -----------------------------------
# 17. Show analysis result
# -----------------------------------

print("\nRental gap by month:")

print(
    gap_by_time
)


# -----------------------------------
# 18. Save joined data
# -----------------------------------

analysis_data.to_csv(
    JOINED_OUTPUT,
    index=False
)


# -----------------------------------
# 19. Save monthly analysis
# -----------------------------------

gap_by_time.to_csv(
    ANALYSIS_OUTPUT,
    index=False
)


# -----------------------------------
# 20. Confirm saved files
# -----------------------------------

print("\nSaved:")

print(
    JOINED_OUTPUT
)

print(
    ANALYSIS_OUTPUT
)