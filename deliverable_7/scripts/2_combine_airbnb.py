import pandas as pd


# File paths
OLD_AIRBNB_FILE = "input/christchurch_listings_clean.csv"
JULY_FILE = "output/1_listings_july_clean.csv"
AUGUST_FILE = "output/1_listings_august_clean.csv"

OUTPUT_FILE = "output/2_airbnb_combined.csv"


# -----------------------------------
# 1. Read the data
# -----------------------------------

old_airbnb = pd.read_csv(OLD_AIRBNB_FILE)
july = pd.read_csv(JULY_FILE)
august = pd.read_csv(AUGUST_FILE)


print("\n-----------------------------------")
print("Reading Airbnb datasets")
print("-----------------------------------")

print("Previous Airbnb rows:")
print(len(old_airbnb))

print("July rows:")
print(len(july))

print("August rows:")
print(len(august))


# -----------------------------------
# 2. Check columns match
# -----------------------------------

print("\nPrevious Airbnb columns:")
print(old_airbnb.columns.tolist())

print("\nJuly columns:")
print(july.columns.tolist())

print("\nAugust columns:")
print(august.columns.tolist())


if list(old_airbnb.columns) != list(july.columns):
    raise ValueError(
        "Previous Airbnb and July columns do not match."
    )

if list(old_airbnb.columns) != list(august.columns):
    raise ValueError(
        "Previous Airbnb and August columns do not match."
    )


# -----------------------------------
# 3. Check available months
# -----------------------------------

print("\nPrevious Airbnb months:")
print(
    sorted(
        old_airbnb["month_year"]
        .dropna()
        .unique()
    )
)

print("\nJuly month:")
print(july["month_year"].unique())

print("\nAugust month:")
print(august["month_year"].unique())


# -----------------------------------
# 4. Remove old rows without price
# -----------------------------------

before = len(old_airbnb)

old_airbnb = old_airbnb.dropna(
    subset=["price"]
).copy()

after = len(old_airbnb)

print("\nOld Airbnb rows removed because price was missing:")
print(before - after)


# -----------------------------------
# 5. Standardise month_year
# -----------------------------------

old_airbnb["month_year"] = pd.to_datetime(
    old_airbnb["month_year"]
)

july["month_year"] = pd.to_datetime(
    july["month_year"]
)

august["month_year"] = pd.to_datetime(
    august["month_year"]
)


# -----------------------------------
# 6. Combine the datasets
# -----------------------------------

airbnb_combined = pd.concat(
    [
        old_airbnb,
        july,
        august
    ],
    ignore_index=True
)

print("\nCombined rows:")
print(len(airbnb_combined))


# -----------------------------------
# 7. Check duplicates
# -----------------------------------

duplicate_listing_month = (
    airbnb_combined
    .duplicated(
        subset=["id", "month_year"]
    )
    .sum()
)

print("\nDuplicate listing and month combinations:")
print(duplicate_listing_month)

if duplicate_listing_month > 0:
    raise ValueError(
        "Duplicate listing and month combinations found."
    )


# -----------------------------------
# 8. Check missing values
# -----------------------------------

print("\nMissing values after combining:")
print(
    airbnb_combined.isna().sum()
)


# -----------------------------------
# 9. Check final month range
# -----------------------------------

print("\nFinal months:")
print(
    sorted(
        airbnb_combined["month_year"]
        .dt.strftime("%Y-%m")
        .unique()
    )
)


# -----------------------------------
# 10. Save combined data
# -----------------------------------

airbnb_combined.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSaved:")
print(OUTPUT_FILE)

print("Final rows:")
print(len(airbnb_combined))