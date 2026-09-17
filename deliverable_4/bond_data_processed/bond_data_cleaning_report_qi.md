# Rental bond data cleaning report — Qi

Generated: 2026-09-17T22:50:03+12:00

## Files and scope

Input: `/Users/archieg/Desktop/MADS/DATA422 Data Wrangling/05-Assignment/DATA422_FriLab_SO_QW_GS_Project/deliverable_4/bond_data_raw/Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv`

Cleaned CSV: `/Users/archieg/Desktop/MADS/DATA422 Data Wrangling/05-Assignment/DATA422_FriLab_SO_QW_GS_Project/deliverable_4/bond_data_processed/bond_data_clean_qi.csv`

Selected quarterly dates: 2025-10-01, 2026-01-01, 2026-04-01.

Counts refer to dataset rows, not individual bonds or tenancies. No Christchurch geographic selection or Airbnb merge is performed. The raw input is not modified.

## Outcome

Input: **226,080 rows × 12 columns**. Output: **26,991 rows × 12 columns**. Total rows removed: **199,089**.

## Inspection activities

The script inspects dimensions, column names, data types, sample records, missing values, exact duplicates, required fields, timeframe counts, location IDs, unique values, dwelling types and bedroom categories. It also examines missing bedrooms by dwelling type and samples records with missing location IDs or median rent. These inspections do not themselves change values.

| Column | Input type | Output type | Input unique values (including missing) |
| --- | --- | --- | --- |
| TimeFrame | str | str | 26 |
| Location Id | float64 | float64 | 2011 |
| Dwelling Type | str | str | 6 |
| Number Of Beds | str | str | 14 |
| Total Bonds | int64 | int64 | 831 |
| Active Bonds | int64 | int64 | 1666 |
| Closed Bonds | int64 | int64 | 732 |
| Median Rent | float64 | float64 | 1029 |
| Geometric Mean Rent | float64 | float64 | 1435 |
| Upper Quartile Rent | float64 | float64 | 1459 |
| Lower Quartile Rent | float64 | float64 | 1141 |
| Log Std Dev Weekly Rent | float64 | float64 | 8923 |

## Cleaning activities in execution order

| Activity | Rows before | Rows removed | Rows remaining |
| --- | --- | --- | --- |
| Keep selected quarterly dates | 226080 | 198868 | 27212 |
| Remove missing Location Id | 27212 | 94 | 27118 |
| Remove Location Id equal to -99 | 27118 | 127 | 26991 |

Rows outside the selected quarters are excluded first. Missing location IDs are then excluded because they cannot support geographic matching. The special location code -99 is excluded for the same analysis purpose; its exact meaning is not assumed. Removal counts are sequential and do not double-count rows.

## Decisions to retain data

All columns are retained. No missing values are filled, no rent outliers are removed, and no rent values are converted. Missing bedroom values and any remaining missing rent values are retained. There is no duplicate-removal step; duplicates are checked and reported only.

Exact duplicates in input: **0**. Exact duplicates in output: **0**.

## Missing values before and after cleaning

The input counts cover all periods; the output counts cover the retained quarters and locations. A reduction does not indicate imputation.

| Column | Input missing | Output missing |
| --- | --- | --- |
| TimeFrame | 0 | 0 |
| Location Id | 794 | 0 |
| Dwelling Type | 0 | 0 |
| Number Of Beds | 12009 | 858 |
| Total Bonds | 0 | 0 |
| Active Bonds | 0 | 0 |
| Closed Bonds | 0 | 0 |
| Median Rent | 803 | 0 |
| Geometric Mean Rent | 803 | 0 |
| Upper Quartile Rent | 803 | 0 |
| Lower Quartile Rent | 803 | 0 |
| Log Std Dev Weekly Rent | 859 | 0 |

## Retained quarterly coverage

| TimeFrame | Input rows in quarter | Output rows in quarter |
| --- | --- | --- |
| 2025-10-01 | 9459 | 9381 |
| 2026-01-01 | 9255 | 9181 |
| 2026-04-01 | 8498 | 8429 |

## Validation

| Check | Result |
| --- | --- |
| No missing Location Id | PASS |
| No Location Id equal to -99 | PASS |
| Only selected quarters | PASS |
| All original columns retained | PASS |
| Row counts reconcile | PASS |

The output contains records. Passing these checks confirms the stated filters; it does not establish that every retained location is in Christchurch.

## Reproduction

Run `clean_bond_qi.py` and select the input CSV when prompted. The script regenerates `bond_data_clean_qi.csv` and this report in `bond_data_processed/` using the selected input and current filtering rules.
