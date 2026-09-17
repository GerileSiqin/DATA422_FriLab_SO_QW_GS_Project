# Deliverable 4 — Activities and outcomes

Prepared: 17 September 2026  
Project: DATA422_FriLab_SO_QW_GS_Project  
Scope: Deliverable 4 inspection, cleaning, troubleshooting and verification, using the current local files.

## Summary

Deliverable 4 has working cleaning scripts and saved outputs for Airbnb listings and rental bond data. The Airbnb script now reads the cleaned Deliverable 3 file and successfully saves its output after a missing-directory error was fixed. Both saved outputs were checked against the transformations in the current scripts.

The current Airbnb result contains **3,469 rows and 14 columns**, covering **June 2026 only**. The rental bond result contains **27,118 rows and 12 columns**, across three selected quarterly dates. These are separately cleaned datasets; they have not yet been geographically matched or merged for a rental-price and availability comparison.

The earlier Deliverable 4 README describes a different Airbnb input with nine months and 28,795 rows. Those figures do not describe the input currently selected in `clean_listings.py`.

## 1. Input selection and file organisation

The Airbnb source was changed from `deliverable_4/data_processed/christchurch_airbnb_oct2025_jun2026.csv` to the existing cleaned file from Deliverable 3:

`deliverable_3/data_processed/christchurch_airbnb_cleaned.csv`

The input path is resolved from the script location using `Path(__file__).resolve().parents[1]`. The output directory is also resolved from the script location, so the listing script does not depend on a fixed absolute project path or the terminal's working directory.

The selected source has 23 columns, 3,469 unique listing IDs and one `month_year` value, `2026-06`. Its recorded source is `listings-NZ-June26.csv`. This is the actual coverage found in the file, despite the broader period described in the earlier documentation.

The bond script reads:

`deliverable_4/bond_data_raw/Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv`

The raw bond file contains 226,080 rows and 12 columns. Its observed `TimeFrame` values run from `2020-01-01` to `2026-04-01`; the filename alone should not be used to infer coverage. The existing README attributes the dataset to Tenancy Services. This report verifies the local files and does not independently recheck the external source or its publication status.

## 2. Airbnb inspection and cleaning completed

The listing script performs the following activities:

1. Reads the selected CSV and prints its row and column counts.
2. Inspects column names, data types and missing values.
3. Checks exact duplicate rows and removes any found.
4. Checks missing latitude and longitude values.
5. Summarises prices, room types, neighbourhood groups and month counts.
6. Investigates missing prices by month and room type.
7. Reviews the 20 highest-priced records and calculates the 90th, 95th, 99th, 99.5th and 99.9th price percentiles.
8. Removes nine columns not retained for the planned comparison.
9. Retains missing prices, missing minimum-night values and high prices without imputation or outlier removal.
10. Prints the final missing-value counts and saves the cleaned CSV.

### Cleaning decisions and current results

| Activity or decision | Verified result |
| --- | --- |
| Exact duplicate check | 0 duplicates; 0 rows removed |
| Latitude and longitude check | 0 missing values in either column |
| Remove nine selected columns | 23 input columns reduced to 14 |
| Retain missing prices | 274 missing values retained |
| Retain missing minimum nights | 2 missing values retained |
| Retain high prices | Highest observed price is 6,277; no price-based row exclusion |
| Preserve input records | All 3,469 rows retained |

The removed columns are `name`, `host_id`, `host_name`, `neighbourhood_group`, `number_of_reviews`, `last_review`, `reviews_per_month`, `number_of_reviews_ltm` and `license`. The location group is constant in the selected input, and `license` is entirely missing. The other removals follow the existing script's planned price and availability focus.

The final columns are:

`month_year`, `source_file`, `id`, `neighbourhood`, `latitude`, `longitude`, `room_type`, `price`, `minimum_nights`, `calculated_host_listings_count`, `availability_365`, `snapshot_date`, `last_review_after_snapshot`, `days_since_last_review`.

Four retained provenance or quality fields—`source_file`, `snapshot_date`, `last_review_after_snapshot` and `days_since_last_review`—explain why the current result has 14 columns rather than the 10 listed in the older README.

### Descriptive checks

| Measure | Current value |
| --- | ---: |
| Non-missing prices | 3,195 |
| Mean price | 250.21 |
| Median price | 214.00 |
| Minimum price | 32.00 |
| Maximum price | 6,277.00 |
| Entire home/apartment listings | 2,735 |
| Private-room listings | 705 |
| Hotel-room listings | 25 |
| Shared-room listings | 4 |

Prices are reported in the source `price` field's units; they are not adjusted or converted to the bond rent period in this work. Means and medians exclude missing prices.

The Deliverable 3 input already contains 47 reviews flagged as occurring after their snapshot date. Deliverable 4 preserves that flag. The 362 missing `days_since_last_review` values comprise 315 missing review dates and those 47 flagged dates. These quality checks were inherited from Deliverable 3, not newly performed as cleaning rules by Deliverable 4.

## 3. Rental bond inspection and cleaning completed

The bond script inspects dimensions, column names, data types, sample records, missing values, exact duplicates, unique values, dwelling types and bedroom counts. It checks that `Location Id` and `TimeFrame` exist, inspects their missing values and investigates rows with missing location or median rent.

The cleaning then:

1. Keeps `TimeFrame` values `2025-10-01`, `2026-01-01` and `2026-04-01`.
2. Removes records with missing `Location Id`.
3. Retains missing `Number Of Beds` values without filling them.
4. Keeps all 12 original columns.
5. Creates the processed-output folder if necessary and saves the cleaned CSV.

| Stage | Rows | Columns |
| --- | ---: | ---: |
| Raw bond data | 226,080 | 12 |
| After selecting three quarterly dates | 27,212 | 12 |
| After removing missing Location Id | 27,118 | 12 |

The period filter removes 198,868 records. Removing missing location IDs removes a further 94 records. The final output retains 876 missing bedroom values, has no missing median rent values, and has no exact duplicate rows. The script checks duplicates but contains no duplicate-removal step; the current input has none.

| Retained TimeFrame | Saved rows |
| --- | ---: |
| 2025-10-01 | 9,427 |
| 2026-01-01 | 9,222 |
| 2026-04-01 | 8,469 |
| Total | 27,118 |

`TimeFrame` identifies the period; `Location Id` identifies the geographic area. The existing README incorrectly describes `Location Id` as showing the quarter in one explanation. No Christchurch geographic filter is implemented in the current bond script, so this output must not be described as Christchurch-only. Counts in this report are counts of bond dataset rows, not sums of bonds or numbers of individual tenancies.

## 4. Error diagnosis and repair completed

Running the listing script initially failed when pandas tried to save into the nonexistent `deliverable_4/data_processed` directory:

`OSError: Cannot save file into a non-existent directory`

The save step now creates the destination directory before writing:

```python
output_file = data_folder / "christchurch_listings_clean.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)
```

The output folder definition and accompanying comments were also updated to describe its purpose correctly. The listing script was executed successfully with the project's `.venv/bin/python`. The saved CSV was reopened and its dimensions verified.

## 5. Verification and saved outputs

Two additional read-only checks reproduced the current cleaning transformations in memory and compared the results with the saved CSVs using `pandas.testing.assert_frame_equal`. Both comparisons passed, covering values, columns and row order.

| Output | Verified dimensions | Verification |
| --- | --- | --- |
| `data_processed/christchurch_listings_clean.csv` | 3,469 × 14 | Listing script executed successfully; saved data exactly matches duplicate removal and nine-column removal applied to its input |
| `bond_data_processed/bond_data_clean.csv` | 27,118 × 12 | Existing saved data exactly matches the selected-quarter and missing-location filters applied to the raw bond file |

The bond script was inspected, and its output was independently reconciled; it was not rerun to overwrite the bond output during this report preparation. No geographic join, price-period conversion, comparative model or new comparison chart was produced.

## 6. Documentation differences and remaining work

The current results supersede the older README's Airbnb figures for this selected input:

| Item | Earlier README | Current verified files |
| --- | --- | --- |
| Airbnb period | October 2025–June 2026 | June 2026 only |
| Airbnb input | 28,795 × 19 | 3,469 × 23 |
| Airbnb output | 28,795 × 10 | 3,469 × 14 |
| Missing prices retained | 10,667 | 274 |
| Missing minimum nights retained | 37 | 2 |

The listing script still contains explanatory comments about three entire months having missing prices and 37 missing minimum-night values. Those comments belong to the older dataset and do not describe the current input. This report records the discrepancy; it does not silently revise those historical explanations or infer why the current June prices are missing.

Before the planned comparison can be completed:

- Agree on the time scope: restore the intended monthly Airbnb coverage if nine months are required, or redesign the comparison around the available June snapshot. The currently selected datasets do not provide matching nine-month coverage.
- Map Airbnb coordinates or neighbourhoods to the bond dataset's geographic identifiers and select the appropriate Christchurch bond records.
- Establish comparable time aggregation and price units before comparing listing prices with bond rents.
- Define a meaningful availability comparison. Airbnb `availability_365` and bond count fields measure different things and should not be treated as interchangeable.
- Update the README and stale script comments to the agreed input, period and verified results. The bond script's absolute path also remains machine-specific.

No completion claim is made here for the combined analysis or any submission. The completed work is the inspection, cleaning, saved outputs, listing-path repair and verification described above.

## 7. Evidence and reproduction

Evidence reviewed: `clean_listings.py`, `clean_bond.py`, `README.md`, both current Deliverable 4 output CSVs, the local raw bond CSV, and the selected Deliverable 3 input and cleaning report. Counts and missingness were recalculated from the current local files on the report preparation date.

From the project root, the scripts can be run using:

```bash
.venv/bin/python deliverable_4/clean_listings.py
.venv/bin/python deliverable_4/clean_bond.py
```

These commands regenerate their respective outputs. The bond script requires its configured absolute project directory to exist. All report findings are limited to the local evidence inspected.
