"""Clean the combined Christchurch Airbnb dataset without changing the raw files."""

from pathlib import Path

import pandas as pd


# Locate the project folders from this script's position.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = PROJECT_ROOT / "deliverable_3" / "data_processed"
OUTPUT_DIR = PROJECT_ROOT / "deliverable_3" / "outputs" / "cleaning"

INPUT_FILE = DATA_PROCESSED / "christchurch_airbnb_oct2025_jun2026.csv"
CLEAN_FILE = DATA_PROCESSED / "christchurch_airbnb_cleaned.csv"
REPORT_FILE = OUTPUT_DIR / "data_cleaning_report.csv"


# The date on which each monthly Airbnb snapshot was collected.
SNAPSHOT_DATES = {
    "2025-10": "2025-10-05",
    "2025-11": "2025-11-07",
    "2025-12": "2025-12-11",
    "2026-01": "2026-01-16",
    "2026-02": "2026-02-13",
    "2026-03": "2026-03-17",
    "2026-04": "2026-04-16",
    "2026-05": "2026-05-23",
    "2026-06": "2026-06-19",
}


def add_report(report: list[dict], check: str, count: int, action: str) -> None:
    """Add one result to the cleaning report."""
    report.append({"check": check, "rows_affected": int(count), "action": action})


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Keep a record of every cleaning rule and how many rows it affected.
    report: list[dict] = []
    data = pd.read_csv(INPUT_FILE, low_memory=False)
    starting_rows = len(data)

    # 1. Standardise column names.
    data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")

    # 2. Remove completely empty rows and exact duplicate rows.
    empty_rows = int(data.isna().all(axis=1).sum())
    data = data.dropna(how="all").copy()
    add_report(report, "Completely empty rows", empty_rows, "Removed")

    exact_duplicates = int(data.duplicated().sum())
    data = data.drop_duplicates().copy()
    add_report(report, "Exact duplicate rows", exact_duplicates, "Removed")

    # 3. Remove duplicate listing IDs within the same monthly snapshot.
    duplicate_keys = int(data.duplicated(["month_year", "id"], keep="first").sum())
    data = data.drop_duplicates(["month_year", "id"], keep="first").copy()
    add_report(
        report,
        "Duplicate month_year + id",
        duplicate_keys,
        "Kept the first row",
    )

    # 4. Trim whitespace in text columns and convert empty strings to missing.
    text_columns = data.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        data[column] = data[column].astype("string").str.strip()
        data[column] = data[column].replace("", pd.NA)

    # 5. Convert fields that should be numeric.
    numeric_columns = [
        "id",
        "host_id",
        "latitude",
        "longitude",
        "price",
        "minimum_nights",
        "number_of_reviews",
        "reviews_per_month",
        "calculated_host_listings_count",
        "availability_365",
        "number_of_reviews_ltm",
    ]
    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    # 6. Convert last_review to a real date.
    data["last_review"] = pd.to_datetime(data["last_review"], errors="coerce")

    # 7. Replace impossible numeric values with missing values.
    invalid_rules = {
        "price": data["price"].lt(0),
        "minimum_nights": data["minimum_nights"].lt(1),
        "number_of_reviews": data["number_of_reviews"].lt(0),
        "reviews_per_month": data["reviews_per_month"].lt(0),
        "calculated_host_listings_count": data[
            "calculated_host_listings_count"
        ].lt(0),
        "availability_365": ~data["availability_365"].between(0, 365),
        "number_of_reviews_ltm": data["number_of_reviews_ltm"].lt(0),
        "latitude": ~data["latitude"].between(-48, -34),
        "longitude": ~data["longitude"].between(166, 179),
    }
    for column, invalid in invalid_rules.items():
        invalid = invalid.fillna(False)
        add_report(
            report,
            f"Invalid {column}",
            int(invalid.sum()),
            "Changed to missing",
        )
        data.loc[invalid, column] = pd.NA

    # 8. Keep only Christchurch City, as required by the assignment.
    outside_christchurch = ~data["neighbourhood_group"].eq("Christchurch City")
    add_report(
        report,
        "Rows outside Christchurch City",
        int(outside_christchurch.sum()),
        "Removed",
    )
    data = data.loc[~outside_christchurch].copy()

    # 9. Flag review dates that occur after their source snapshot date.
    data["snapshot_date"] = pd.to_datetime(data["month_year"].map(SNAPSHOT_DATES))
    data["last_review_after_snapshot"] = data["last_review"].gt(
        data["snapshot_date"]
    )
    future_reviews = int(data["last_review_after_snapshot"].sum())
    add_report(
        report,
        "Last review after snapshot date",
        future_reviews,
        "Flagged; original date retained",
    )

    # Calculate elapsed days only for logically valid review dates.
    data["days_since_last_review"] = (
        data["snapshot_date"] - data["last_review"]
    ).dt.days
    data.loc[data["last_review_after_snapshot"], "days_since_last_review"] = pd.NA

    # 10. Save the cleaned data and an auditable cleaning report.
    data = data.sort_values(["month_year", "id"], kind="stable").reset_index(drop=True)
    data.to_csv(CLEAN_FILE, index=False, date_format="%Y-%m-%d")
    pd.DataFrame(report).to_csv(REPORT_FILE, index=False)

    print("Input rows:", f"{starting_rows:,}")
    print("Cleaned rows:", f"{len(data):,}")
    print("Future-dated reviews flagged:", f"{future_reviews:,}")
    print("Cleaned data saved to:", CLEAN_FILE)
    print("Cleaning report saved to:", REPORT_FILE)


if __name__ == "__main__":
    main()
