import pandas as pd


# File paths
JULY_FILE = "input/listings_july.csv"
AUGUST_FILE = "input/listings_august.csv"

JULY_OUTPUT = "output/1_listings_july_clean.csv"
AUGUST_OUTPUT = "output/1_listings_august_clean.csv"


def clean_airbnb(filename, month_year, output_file):
    """
    Reads, checks and cleans one month of Airbnb data
    for Christchurch City.
    """

    # -----------------------------------
    # 1. Read the raw data
    # -----------------------------------

    df = pd.read_csv(filename)

    print("\n-----------------------------------")
    print("Reading:", filename)
    print("-----------------------------------")

    print("Shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())


    # -----------------------------------
    # 2. Check required columns
    # -----------------------------------

    required_columns = [
        "id",
        "neighbourhood_group",
        "neighbourhood",
        "latitude",
        "longitude",
        "room_type",
        "price",
        "minimum_nights",
        "calculated_host_listings_count",
        "availability_365"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                "Missing required column: " + column
            )


    # -----------------------------------
    # 3. Filter Christchurch City
    # -----------------------------------

    df = df[
        df["neighbourhood_group"] == "Christchurch City"
    ].copy()

    print("\nRows after Christchurch filter:")
    print(len(df))

    if len(df) == 0:
        raise ValueError(
            "No Christchurch City listings found."
        )


    # -----------------------------------
    # 4. Check duplicates
    # -----------------------------------

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nDuplicate listing IDs:")
    print(df["id"].duplicated().sum())


    # -----------------------------------
    # 5. Check missing values
    # -----------------------------------

    print("\nMissing values:")
    print(df[required_columns].isna().sum())


    # -----------------------------------
    # 6. Keep columns needed
    # -----------------------------------

    keep_columns = [
        "id",
        "neighbourhood",
        "latitude",
        "longitude",
        "room_type",
        "price",
        "minimum_nights",
        "calculated_host_listings_count",
        "availability_365"
    ]

    df = df[keep_columns].copy()


    # -----------------------------------
    # 7. Remove rows without price
    # -----------------------------------

    before = len(df)

    df = df.dropna(
        subset=["price"]
    )

    after = len(df)

    print("\nRows removed because price was missing:")
    print(before - after)


    # -----------------------------------
    # 8. Add month
    # -----------------------------------

    df["month_year"] = month_year


    # -----------------------------------
    # 9. Save cleaned data
    # -----------------------------------

    df.to_csv(
        output_file,
        index=False
    )

    print("\nSaved:")
    print(output_file)

    print("Final rows:")
    print(len(df))


# -----------------------------------
# Clean July
# -----------------------------------

clean_airbnb(
    JULY_FILE,
    "2026-07-01",
    JULY_OUTPUT
)


# -----------------------------------
# Clean August
# -----------------------------------

clean_airbnb(
    AUGUST_FILE,
    "2026-08-01",
    AUGUST_OUTPUT
)