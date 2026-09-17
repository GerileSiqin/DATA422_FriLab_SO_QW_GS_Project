# Christchurch Airbnb cleaning report — Qi

Generated: 2026-09-17T23:02:58+12:00

## Files and scope

Input: `/Users/archieg/Desktop/MADS/DATA422 Data Wrangling/05-Assignment/DATA422_FriLab_SO_QW_GS_Project/deliverable_3/data_processed/christchurch_airbnb_cleaned.csv`

Cleaned CSV: `/Users/archieg/Desktop/MADS/DATA422 Data Wrangling/05-Assignment/DATA422_FriLab_SO_QW_GS_Project/deliverable_4/data_processed/christchurch_listings_clean_qi.csv`

The raw input file was read only and was not modified.

## Outcome

Input: **3,469 rows × 23 columns**. Output: **3,469 rows × 13 columns**. Exact duplicate rows removed: **0**. Columns removed: **10**.

## Inspection activities

The script inspected the dataset dimensions, column names, data types, missing values, exact duplicates, latitude and longitude, price statistics, room types, neighbourhood groups, monthly coverage, missing-price patterns, the highest prices and selected price percentiles.

| Column | Input type | Output type |
| --- | --- | --- |
| month_year | str | str |
| source_file | str | Removed |
| id | int64 | int64 |
| name | str | str |
| host_id | float64 | float64 |
| host_name | str | str |
| neighbourhood_group | str | Removed |
| neighbourhood | str | str |
| latitude | float64 | float64 |
| longitude | float64 | float64 |
| room_type | str | str |
| price | float64 | float64 |
| minimum_nights | float64 | float64 |
| number_of_reviews | float64 | Removed |
| last_review | str | Removed |
| reviews_per_month | float64 | Removed |
| calculated_host_listings_count | float64 | float64 |
| availability_365 | float64 | float64 |
| number_of_reviews_ltm | float64 | Removed |
| license | float64 | Removed |
| snapshot_date | str | Removed |
| last_review_after_snapshot | bool | Removed |
| days_since_last_review | float64 | Removed |

## Cleaning activities

Exact duplicate rows were checked and removed: **0**. No additional rows were removed. Missing prices and missing minimum-night values were retained, and high prices were inspected without applying an outlier-removal rule.

The following columns were removed because they are outside the retained listing, host, location, price and availability fields:

- `neighbourhood_group`
- `number_of_reviews`
- `last_review`
- `reviews_per_month`
- `number_of_reviews_ltm`
- `license`
- `source_file`
- `snapshot_date`
- `last_review_after_snapshot`
- `days_since_last_review`

The identifying fields `name`, `host_id` and `host_name` were retained as requested.

## Final columns

- `month_year`
- `id`
- `name`
- `host_id`
- `host_name`
- `neighbourhood`
- `latitude`
- `longitude`
- `room_type`
- `price`
- `minimum_nights`
- `calculated_host_listings_count`
- `availability_365`

## Missing values before and after cleaning

Missing values were not filled. ‘Removed’ means that the entire column was excluded from the output.

| Column | Input missing | Output missing |
| --- | --- | --- |
| month_year | 0 | 0 |
| source_file | 0 | Removed |
| id | 0 | 0 |
| name | 0 | 0 |
| host_id | 0 | 0 |
| host_name | 0 | 0 |
| neighbourhood_group | 0 | Removed |
| neighbourhood | 0 | 0 |
| latitude | 0 | 0 |
| longitude | 0 | 0 |
| room_type | 0 | 0 |
| price | 274 | 274 |
| minimum_nights | 2 | 2 |
| number_of_reviews | 0 | Removed |
| last_review | 315 | Removed |
| reviews_per_month | 315 | Removed |
| calculated_host_listings_count | 0 | 0 |
| availability_365 | 0 | 0 |
| number_of_reviews_ltm | 0 | Removed |
| license | 3469 | Removed |
| snapshot_date | 0 | Removed |
| last_review_after_snapshot | 0 | Removed |
| days_since_last_review | 362 | Removed |

## Retained monthly coverage

| month_year | Rows |
| --- | --- |
| 2026-06 | 3469 |

## Validation

| Check | Result |
| --- | --- |
| All requested columns removed | PASS |
| name retained | PASS |
| host_id retained | PASS |
| host_name retained | PASS |
| No exact duplicate rows | PASS |
| Latitude has no missing values | PASS |
| Longitude has no missing values | PASS |

## Reproduction

Run `clean_listing_qi.py`, then enter a CSV file path, a folder containing the expected CSV, or press Enter to use the displayed default. The script regenerates the cleaned CSV and this report in `data_processed/`.
