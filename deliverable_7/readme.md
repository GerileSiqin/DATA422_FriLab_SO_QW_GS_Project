# DATA422 Deliverable 7 — Automated Airbnb + Bond Pipeline

## Research question

**How does the gap between Airbnb nightly prices and long-term daily rent change over time in Christchurch?**

The pipeline also updates the previous Airbnb price analysis by comparing the median Airbnb nightly price for Christchurch overall and Christchurch Central, including the new July and August 2026 data.

## Required data

The pipeline uses four input files:

- `listings_july.csv` — July 2026 New Zealand Airbnb listings
- `listings_august.csv` — August 2026 New Zealand Airbnb listings
- `christchurch_listings_clean.csv` — previously cleaned Christchurch Airbnb data
- `bond_data_clean.csv` — previously cleaned long-term rental Bond data

## Pipeline overview

The pipeline contains **5 main scripts**.

### 1. `1_clean_new_airbnb.py`

**Purpose:** Clean the new July and August Airbnb datasets.

**Main steps:**

- Read July and August Airbnb data
- Check required columns
- Filter to Christchurch City
- Check for duplicate rows and repeated Airbnb listing IDs (`id`)
- Check missing values
- Remove rows with missing `price`
- Add `month_year`
- Save cleaned July and August files

**Outputs:**

- `1_listings_july_clean.csv`
- `1_listings_august_clean.csv`

### 2. `2_combine_airbnb.py`

**Purpose:** Combine the new Airbnb data with the previous Christchurch Airbnb data.

**Main steps:**

- Read the previous cleaned Christchurch Airbnb data
- Read the cleaned July and August Airbnb data
- Check that the columns match
- Remove previous rows with missing `price`
- Make sure `month_year` uses the same date format in all Airbnb files
- Combine previous Airbnb data with July and August 2026
- Check that each `id + month_year` combination is unique, so the same Airbnb listing is not repeated in the same month
- Save one combined Airbnb dataset

**Output:**

- `2_airbnb_combined.csv`

### 3. `3_prepare_join.py`

**Purpose:** Prepare Airbnb data so it can be analysed and joined with the Bond data.

**Main steps:**

- Read the combined Airbnb dataset
- Read the Koordinates API key from the local `api_key.txt` file
- Use latitude and longitude with the Koordinates API
- Add SA2 `location_id` and `location_name`
- Convert Airbnb `month_year` to quarter-start `TimeFrame` so it can be matched with the quarterly Bond data
- Check whether each Airbnb quarter has a matching quarter in the Bond data
- Save Airbnb data ready for analysis and joining

**Output:**

- `3_airbnb_ready_for_join.csv`

The `api_key.txt` file is stored locally and is excluded from GitHub using `.gitignore`.

### 4. `4_analyse.py`

**Purpose:** Update the Airbnb price analysis and calculate the Airbnb–Bond rental-price gap.

**Main steps:**

**Airbnb price analysis:**

- Calculate the median Airbnb nightly price for each month in Christchurch overall
- Calculate the median Airbnb nightly price for each month in Christchurch Central (`location_id = 326600`)
- Include the new July and August 2026 Airbnb data
- Save the monthly Airbnb price results

**Airbnb–Bond rental-gap analysis:**

- Check required Airbnb and Bond columns
- Make sure the join columns use matching data types before joining Airbnb and Bond data
- Filter Bond data to overall rental summaries: `Dwelling Type = ALL` and `Number Of Beds = ALL`
- Check that each Bond `Location Id + TimeFrame` combination is unique
- Inner join Airbnb and Bond using SA2 location and `TimeFrame`
- Convert weekly Bond rent to a daily equivalent
- Calculate the rental gap
- Calculate the median rental gap for each Airbnb month

**Calculations:**

- Long-term daily rent = Median Rent / 7

- Rental gap = Airbnb nightly price - Long-term daily rent

A positive rental gap means the Airbnb nightly price is higher than the daily equivalent of the long-term rent.

**Outputs:**

- `4_airbnb_price_by_time.csv`
- `4_airbnb_bond_joined.csv`
- `4_rental_gap_by_time.csv`

### 5. `5_create_plots.py`

**Purpose:** Create the updated visualisations.

**Main steps:**

- Read the monthly Airbnb price results
- Create a line plot comparing the median Airbnb nightly price for Christchurch overall and Christchurch Central
- Read the monthly rental-gap results
- Create a line plot of the median rental gap over time
- Save both plots

**Outputs:**

- `5_airbnb_price_over_time.png`
- `5_rental_gap_over_time.png`

## Updated Airbnb analysis

The updated Airbnb price analysis includes the new July and August 2026 data.

For Christchurch overall:

- July 2026 median Airbnb price = $227 per night
- August 2026 median Airbnb price = $224 per night

For Christchurch Central:

- July 2026 median Airbnb price = $253 per night
- August 2026 median Airbnb price = $256 per night

This updates the previous Christchurch Central Airbnb price analysis and also compares Christchurch Central with Christchurch overall.

## Why the updated analysis was chosen

In Deliverable 5, our team also compared Airbnb listings with active rental bonds by location and analysed the largest short-term versus long-term rental price gaps.

These analyses require Airbnb and Bond data from matching time periods. The available Bond dataset does not contain the Q3 2026 quarter, so July and August 2026 cannot be added to those analyses correctly.

Therefore, the Christchurch Central median Airbnb price analysis was updated instead and expanded to compare Christchurch Central with Christchurch overall. This allows the new July and August data to be included without mixing unmatched time periods.

## Answer to the research question

The gap between Airbnb nightly prices and long-term daily rent was higher in **March–June 2026** than in **October–November 2025**. Within the available 2026 months, the gap decreased from March to May and then remained stable in June. This shows that the difference between short-term Airbnb prices and long-term daily-equivalent rent changed over time rather than remaining constant.

July and August 2026 cannot be included in the Airbnb–Bond rental-gap analysis because the Bond dataset has no matching `2026-07-01` quarter.

## Main limitations

- Airbnb and long-term residential rentals are different markets, so their prices are not directly equivalent.
- Bond `Median Rent` is weekly and is divided by 7 to create a daily equivalent for comparison with Airbnb nightly prices.
- Bond data is quarterly while Airbnb data is monthly.
- Airbnb price data is missing for December 2025, January 2026, and February 2026.
- July and August 2026 are included in the updated Airbnb price analysis, but they cannot be included in the Airbnb–Bond rental-gap analysis because the Bond dataset has no matching `2026-07-01` quarter.
- Linear regression was not used for the rental-gap analysis because there are only six usable monthly observations and there is a three-month data gap.

## Automation and orchestration

`run_pipeline.py` is the **orchestration file**.

It runs the five scripts in the correct order:

- `1_clean_new_airbnb.py`
- `2_combine_airbnb.py`
- `3_prepare_join.py`
- `4_analyse.py`
- `5_create_plots.py`

The orchestration file uses:

- `subprocess.run(..., check=True)`

This means that if one stage fails, the pipeline stops instead of continuing with incorrect or incomplete data.

The updated pipeline automatically produces both the Airbnb price analysis and the Airbnb–Bond rental-gap analysis, together with their updated plots.

## Run the pipeline from the command line

Example using PowerShell:

- `conda activate ds`
- `cd "path\to\deliverable_7"`
- `python run_pipeline.py`

During Step 3, the Koordinates API key is automatically read from the local `api_key.txt` file.

The `api_key.txt` file is excluded from GitHub using `.gitignore`, so the API key is not stored in the shared repository.

## Dependencies

### External packages

- **Python 3.12.13** — runs all pipeline scripts
- **pandas** — reads, cleans, combines, joins, and summarises the data
- **matplotlib** — creates the final plots
- **requests** — sends requests to the Koordinates API

### Python standard library

- **ThreadPoolExecutor** — speeds up multiple Koordinates API requests
- **subprocess** — runs the five scripts from `run_pipeline.py`
- **sys** — makes sure the pipeline uses the same Python environment

### Other requirement

- **Koordinates API key** — gives access to SA2 location data
- **`api_key.txt`** — stores the API key locally and is excluded from GitHub using `.gitignore`

The project was run in the Conda environment called `ds`.

## Data sources

### Airbnb data

- Inside Airbnb — New Zealand listings  
https://insideairbnb.com/get-the-data/

### Long-term rental data

- Tenancy Services — Bond rental data  
https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/

### SA2 geographic data

- Stats NZ / Koordinates Datafinder — SA2 2026 geographic areas  
https://datafinder.stats.govt.nz/