"""Prepare and summarise the Deliverable 3 Christchurch Airbnb data.

Put every monthly listings CSV (October 2025 to June 2026) in:
    deliverable_3/data_raw/

Then run this file. It filters each file to Christchurch City, adds a month,
combines the monthly data, and writes the processed data and summaries.
"""

from pathlib import Path
import re

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "deliverable_3" / "data_raw"
PROCESSED_DIR = PROJECT_ROOT / "deliverable_3" / "data_processed"
SUMMARY_DIR = PROJECT_ROOT / "deliverable_3" / "outputs" / "summary_tables"

START_MONTH = pd.Period("2025-10", freq="M")
END_MONTH = pd.Period("2026-06", freq="M")
CHRISTCHURCH_VALUE = "Christchurch City"

MONTH_NUMBERS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def month_from_filename(file_path: Path) -> pd.Period:
    """Extract a month from names like June26, 2026-06, or 19062026."""
    stem = file_path.stem

    named_month = re.search(
        r"(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[-_ ]?(\d{2}|\d{4})(?!\d)",
        stem,
    )
    if named_month:
        month = MONTH_NUMBERS[named_month.group(1).lower()]
        year_text = named_month.group(2)
        year = int(year_text) if len(year_text) == 4 else 2000 + int(year_text)
        return pd.Period(year=year, month=month, freq="M")

    year_month = re.search(r"(20\d{2})[-_](0[1-9]|1[0-2])", stem)
    if year_month:
        return pd.Period(
            year=int(year_month.group(1)),
            month=int(year_month.group(2)),
            freq="M",
        )

    day_month_year = re.search(r"(?:^|\D)\d{2}(0[1-9]|1[0-2])(20\d{2})(?:\D|$)", stem)
    if day_month_year:
        return pd.Period(
            year=int(day_month_year.group(2)),
            month=int(day_month_year.group(1)),
            freq="M",
        )

    raise ValueError(
        f"Cannot identify the month from {file_path.name}. "
        "Include a date such as June26, 2026-06, or 19062026 in the filename."
    )


def find_monthly_files() -> list[tuple[pd.Period, Path]]:
    """Find monthly listing CSVs and retain the assignment date range."""
    dated_files = []
    for file_path in sorted(RAW_DIR.glob("listings*.csv")):
        month = month_from_filename(file_path)
        if START_MONTH <= month <= END_MONTH:
            dated_files.append((month, file_path))

    if not dated_files:
        raise FileNotFoundError(f"No listings CSV files found in {RAW_DIR}")

    months = [month for month, _ in dated_files]
    duplicates = sorted({str(month) for month in months if months.count(month) > 1})
    if duplicates:
        raise ValueError(f"More than one CSV was found for month(s): {', '.join(duplicates)}")

    return sorted(dated_files, key=lambda item: item[0])


def prepare_data(monthly_files: list[tuple[pd.Period, Path]]) -> pd.DataFrame:
    """Load, validate, filter, label, and concatenate all monthly files."""
    prepared_months = []

    for month, file_path in monthly_files:
        raw = pd.read_csv(file_path, low_memory=False)
        if "neighbourhood_group" not in raw.columns:
            raise KeyError(f"{file_path.name} has no 'neighbourhood_group' column")

        christchurch = raw.loc[
            raw["neighbourhood_group"].eq(CHRISTCHURCH_VALUE)
        ].copy()
        christchurch.insert(0, "month_year", str(month))
        christchurch.insert(1, "source_file", file_path.name)
        prepared_months.append(christchurch)

        print(
            f"{month}: {len(raw):,} NZ rows -> "
            f"{len(christchurch):,} Christchurch rows ({file_path.name})"
        )

    return pd.concat(prepared_months, ignore_index=True, sort=False)


def save_summaries(data: pd.DataFrame) -> None:
    """Create numeric, categorical, missing-value, and monthly summaries."""
    missing = pd.DataFrame(
        {
            "column": data.columns,
            "missing_count": data.isna().sum().to_numpy(),
            "missing_percent": (data.isna().mean().to_numpy() * 100).round(2),
        }
    )
    missing.to_csv(SUMMARY_DIR / "missing_values_summary.csv", index=False)

    numeric = data.select_dtypes(include="number")
    numeric_summary = numeric.describe().T
    numeric_summary["missing_count"] = numeric.isna().sum()
    numeric_summary.to_csv(SUMMARY_DIR / "numeric_summary_statistics.csv")

    categorical = data.select_dtypes(exclude="number")
    categorical_rows = []
    for column in categorical.columns:
        counts = categorical[column].value_counts(dropna=True)
        categorical_rows.append(
            {
                "column": column,
                "non_missing_count": int(categorical[column].notna().sum()),
                "missing_count": int(categorical[column].isna().sum()),
                "unique_count": int(categorical[column].nunique(dropna=True)),
                "most_common_value": counts.index[0] if not counts.empty else pd.NA,
                "most_common_count": int(counts.iloc[0]) if not counts.empty else 0,
            }
        )
    pd.DataFrame(categorical_rows).to_csv(
        SUMMARY_DIR / "categorical_summary_statistics.csv", index=False
    )

    data.groupby("month_year", sort=True).size().rename("listing_count").to_csv(
        SUMMARY_DIR / "listings_by_month.csv"
    )


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    monthly_files = find_monthly_files()
    expected_months = set(pd.period_range(START_MONTH, END_MONTH, freq="M"))
    found_months = {month for month, _ in monthly_files}
    missing_months = sorted(expected_months - found_months)

    print(f"Found {len(monthly_files)} of 9 required monthly files.")
    if missing_months:
        print("Still needed:", ", ".join(str(month) for month in missing_months))

    combined = prepare_data(monthly_files)
    output_file = PROCESSED_DIR / "christchurch_airbnb_oct2025_jun2026.csv"
    combined.to_csv(output_file, index=False)
    save_summaries(combined)

    print(f"\nCombined data shape: {combined.shape}")
    print(f"Combined data saved to: {output_file}")
    print(f"Summary tables saved to: {SUMMARY_DIR}")


if __name__ == "__main__":
    main()
