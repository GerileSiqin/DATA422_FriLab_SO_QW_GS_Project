"""
Prepare combined Airbnb data for joining with Bond data.

This script:
1. Reads the combined Airbnb data and cleaned Bond data.
2. Reads the Koordinates API key from api_key.txt.
3. Gets SA2 location codes and names from the Koordinates API.
4. Converts Airbnb month_year to quarter-start TimeFrame.
5. Checks whether Airbnb quarters match available Bond quarters.
6. Saves the Airbnb data ready for analysis and joining.

Author: Gerile
"""

from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests


# -----------------------------------
# File paths
# -----------------------------------

AIRBNB_FILE = "output/2_airbnb_combined.csv"
BOND_FILE = "input/bond_data_clean.csv"

API_KEY_FILE = "api_key.txt"

OUTPUT_FILE = "output/3_airbnb_ready_for_join.csv"


# -----------------------------------
# Koordinates API settings
# -----------------------------------

LAYER_ID = 123515

API_URL = (
    "https://datafinder.stats.govt.nz/"
    "services/query/v1/vector.json"
)

WORKERS = 4


# -----------------------------------
# Function: read API key
# -----------------------------------

def read_api_key():
    """Read the Koordinates API key from api_key.txt."""

    try:

        with open(
            API_KEY_FILE,
            "r"
        ) as file:

            api_key = file.read().strip()

    except FileNotFoundError:

        raise ValueError(
            "api_key.txt was not found."
        )


    if not api_key:

        raise ValueError(
            "api_key.txt is empty."
        )


    return api_key


# -----------------------------------
# Function: get SA2 area
# -----------------------------------

def get_area_code(latitude, longitude, api_key):
    """Return SA2 location ID and name for one Airbnb location."""

    params = {
        "key": api_key,
        "layer": LAYER_ID,
        "x": longitude,
        "y": latitude,
        "max_results": 3,
        "radius": 10000,
        "geometry": "false",
        "with_field_names": "true"
    }

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        features = (
            data["vectorQuery"]
            ["layers"]
            [str(LAYER_ID)]
            ["features"]
        )

        for feature in features:

            if feature.get("distance") == 0:

                properties = feature["properties"]

                location_id = properties.get(
                    "SA22026_V1_00"
                )

                location_name = properties.get(
                    "SA22026_V1_00_NAME"
                )

                return location_id, location_name

    except Exception as error:

        print(
            f"API error for "
            f"{latitude}, {longitude}: {error}"
        )


    return None, None


# -----------------------------------
# Function: query one location
# -----------------------------------

def query_location(row, api_key):
    """Query one latitude and longitude pair."""

    latitude = row["latitude"]
    longitude = row["longitude"]

    location_id, location_name = get_area_code(
        latitude,
        longitude,
        api_key
    )

    return (
        latitude,
        longitude,
        location_id,
        location_name
    )


# -----------------------------------
# Main program
# -----------------------------------

def main():

    print("\n===================================")
    print("Preparing Airbnb data for joining")
    print("===================================")


    # -----------------------------------
    # Read data
    # -----------------------------------

    airbnb = pd.read_csv(
        AIRBNB_FILE
    )

    bond = pd.read_csv(
        BOND_FILE
    )


    print("\nAirbnb rows:")
    print(len(airbnb))

    print("\nBond rows:")
    print(len(bond))


    # -----------------------------------
    # Check required columns
    # -----------------------------------

    required_airbnb_columns = [
        "id",
        "latitude",
        "longitude",
        "price",
        "month_year"
    ]

    required_bond_columns = [
        "Location Id",
        "TimeFrame"
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
    # Read Koordinates API key
    # -----------------------------------

    api_key = read_api_key()

    print(
        "\nKoordinates API key loaded "
        "from api_key.txt."
    )


    # -----------------------------------
    # Find unique coordinates
    # -----------------------------------

    unique_locations = (
        airbnb[
            ["latitude", "longitude"]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )


    print("\nUnique latitude/longitude pairs:")
    print(len(unique_locations))


    # -----------------------------------
    # Get SA2 codes
    # -----------------------------------

    print("\nGetting SA2 area codes...")


    def run_query(row):

        return query_location(
            row,
            api_key
        )


    rows = [
        row
        for _, row
        in unique_locations.iterrows()
    ]


    with ThreadPoolExecutor(
        max_workers=WORKERS
    ) as executor:

        results = list(
            executor.map(
                run_query,
                rows
            )
        )


    # -----------------------------------
    # Create location mapping
    # -----------------------------------

    location_mapping = pd.DataFrame(
        results,
        columns=[
            "latitude",
            "longitude",
            "location_id",
            "location_name"
        ]
    )


    # -----------------------------------
    # Merge SA2 data back to Airbnb
    # -----------------------------------

    airbnb = airbnb.merge(
        location_mapping,
        on=[
            "latitude",
            "longitude"
        ],
        how="left"
    )


    # -----------------------------------
    # Check missing SA2 values
    # -----------------------------------

    missing_codes = (
        airbnb["location_id"]
        .isna()
        .sum()
    )

    missing_names = (
        airbnb["location_name"]
        .isna()
        .sum()
    )


    print("\nMissing SA2 codes:")
    print(missing_codes)

    print("\nMissing SA2 names:")
    print(missing_names)


    if missing_codes > 0:

        raise ValueError(
            "Some Airbnb rows are missing SA2 codes."
        )


    # -----------------------------------
    # Prepare Airbnb month
    # -----------------------------------

    airbnb["month_year"] = pd.to_datetime(
        airbnb["month_year"]
    )


    # -----------------------------------
    # Convert Airbnb month to quarter
    # -----------------------------------

    airbnb["TimeFrame"] = (
        airbnb["month_year"]
        .dt.to_period("Q")
        .dt.start_time
    )


    # -----------------------------------
    # Prepare Bond time
    # -----------------------------------

    bond["TimeFrame"] = pd.to_datetime(
        bond["TimeFrame"]
    )


    # -----------------------------------
    # Make Airbnb location ID numeric
    # -----------------------------------

    airbnb["location_id"] = pd.to_numeric(
        airbnb["location_id"],
        errors="coerce"
    ).astype("Int64")


    # -----------------------------------
    # Show month-to-quarter mapping
    # -----------------------------------

    month_mapping = (
        airbnb[
            [
                "month_year",
                "TimeFrame"
            ]
        ]
        .drop_duplicates()
        .sort_values(
            "month_year"
        )
    )


    print(
        "\nAirbnb month to quarter mapping:"
    )

    print(
        month_mapping
    )


    # -----------------------------------
    # Show available Bond quarters
    # -----------------------------------

    bond_quarters = (
        bond["TimeFrame"]
        .drop_duplicates()
        .sort_values()
    )


    print("\nBond quarters:")
    print(bond_quarters)


    # -----------------------------------
    # Check unmatched Airbnb quarters
    # -----------------------------------

    airbnb_quarters = (
        airbnb["TimeFrame"]
        .drop_duplicates()
        .sort_values()
    )


    unmatched_quarters = (
        airbnb_quarters[
            ~airbnb_quarters.isin(
                bond_quarters
            )
        ]
    )


    print(
        "\nAirbnb quarters with no matching "
        "Bond quarter:"
    )

    print(
        unmatched_quarters
    )


    # -----------------------------------
    # Save output
    # -----------------------------------

    airbnb.to_csv(
        OUTPUT_FILE,
        index=False
    )


    print("\nSaved:")
    print(OUTPUT_FILE)

    print("\nFinal rows:")
    print(len(airbnb))


# -----------------------------------
# Run program
# -----------------------------------

if __name__ == "__main__":
    main()