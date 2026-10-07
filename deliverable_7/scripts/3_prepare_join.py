import pandas as pd
import requests
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor


# File paths
AIRBNB_FILE = "output/2_airbnb_combined.csv"
BOND_FILE = "input/bond_data_clean.csv"

OUTPUT_FILE = "output/3_airbnb_ready_for_join.csv"


# Koordinates settings
LAYER_ID = 123515

# Number of API requests running at the same time
WORKERS = 4


def get_area_code(latitude, longitude, api_key):
    """
    Returns the SA2 code and name for one Airbnb location.
    """

    url = (
        "https://datafinder.stats.govt.nz/"
        "services/query/v1/vector.json"
    )

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
            url,
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

        return None, None

    except Exception as error:

        print(
            "Query failed for",
            latitude,
            longitude,
            ":",
            error
        )

        return None, None


def query_location(args):
    """
    Runs one SA2 query.
    """

    latitude, longitude, api_key = args

    return get_area_code(
        latitude,
        longitude,
        api_key
    )


def main():

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
    print("Preparing Airbnb data for joining")
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
        "latitude",
        "longitude",
        "price",
        "month_year"
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
        "TimeFrame"
    ]

    for column in required_bond_columns:

        if column not in bond.columns:

            raise ValueError(
                "Missing Bond column: " + column
            )


    # -----------------------------------
    # 4. Enter Koordinates API key
    # -----------------------------------

    api_key = getpass(
        "\nPaste your Koordinates API key: "
    )


    # -----------------------------------
    # 5. Find unique Airbnb locations
    # -----------------------------------

    unique_locations = (
        airbnb[
            [
                "latitude",
                "longitude"
            ]
        ]
        .drop_duplicates()
        .copy()
    )

    print("\nUnique latitude/longitude pairs:")
    print(len(unique_locations))


    # -----------------------------------
    # 6. Prepare API requests
    # -----------------------------------

    query_inputs = [
        (
            latitude,
            longitude,
            api_key
        )

        for latitude, longitude
        in zip(
            unique_locations["latitude"],
            unique_locations["longitude"]
        )
    ]


    # -----------------------------------
    # 7. Get SA2 area codes
    # -----------------------------------

    print("\nGetting SA2 area codes...")

    with ThreadPoolExecutor(
        max_workers=WORKERS
    ) as executor:

        results = list(
            executor.map(
                query_location,
                query_inputs
            )
        )


    # -----------------------------------
    # 8. Add SA2 results
    # -----------------------------------

    unique_locations["location_id"] = [
        result[0]
        for result in results
    ]

    unique_locations["location_name"] = [
        result[1]
        for result in results
    ]


    # -----------------------------------
    # 9. Check missing SA2 results
    # -----------------------------------

    print("\nMissing SA2 codes:")
    print(
        unique_locations[
            "location_id"
        ].isna().sum()
    )

    print("\nMissing SA2 names:")
    print(
        unique_locations[
            "location_name"
        ].isna().sum()
    )


    # -----------------------------------
    # 10. Add SA2 data back to Airbnb
    # -----------------------------------

    airbnb = airbnb.merge(
        unique_locations,
        on=[
            "latitude",
            "longitude"
        ],
        how="left"
    )


    # -----------------------------------
    # 11. Convert month_year to datetime
    # -----------------------------------

    airbnb["month_year"] = pd.to_datetime(
        airbnb["month_year"]
    )


    # -----------------------------------
    # 12. Convert month to quarter start
    # -----------------------------------

    airbnb["TimeFrame"] = (
        airbnb["month_year"]
        .dt.to_period("Q")
        .dt.start_time
    )


    # -----------------------------------
    # 13. Prepare Bond TimeFrame
    # -----------------------------------

    bond["TimeFrame"] = pd.to_datetime(
        bond["TimeFrame"]
    )


    # -----------------------------------
    # 14. Show Airbnb time mapping
    # -----------------------------------

    print("\nAirbnb month to quarter mapping:")

    print(
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


    # -----------------------------------
    # 15. Show Bond quarters
    # -----------------------------------

    bond_quarters = (
        bond["TimeFrame"]
        .drop_duplicates()
        .sort_values()
    )

    print("\nBond quarters:")
    print(bond_quarters)


    # -----------------------------------
    # 16. Check Airbnb quarters
    #     available in Bond
    # -----------------------------------

    airbnb_quarters = (
        airbnb["TimeFrame"]
        .drop_duplicates()
    )

    unmatched_quarters = (
        airbnb_quarters[
            ~airbnb_quarters.isin(
                bond_quarters
            )
        ]
    )

    print(
        "\nAirbnb quarters with no "
        "matching Bond quarter:"
    )

    print(
        unmatched_quarters
        .sort_values()
    )


    # -----------------------------------
    # 17. Prepare location ID type
    # -----------------------------------

    airbnb["location_id"] = pd.to_numeric(
        airbnb["location_id"],
        errors="coerce"
    ).astype("Int64")


    # -----------------------------------
    # 18. Save join-ready Airbnb data
    # -----------------------------------

    airbnb.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nSaved:")
    print(OUTPUT_FILE)

    print("\nFinal rows:")
    print(len(airbnb))


if __name__ == "__main__":
    main()