# DATA422 Deliverable 7 — Automated Airbnb + Bond Pipeline

## Research question

**How does the gap between Airbnb nightly prices and long-term daily rent change over time in Christchurch?**

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
- Check for duplicate rows and repeated Airbnb listing IDs (id)
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

**Purpose:** Prepare Airbnb data so it can be joined with the Bond data.

**Main steps:**

- Read the combined Airbnb dataset
- Use latitude and longitude with the Koordinates API
- Add SA2 `location_id` and `location_name`
- Convert Airbnb `month_year` to quarter-start `TimeFrame` so it can be matched with the quarterly Bond data
- Check whether each Airbnb quarter has a matching quarter in the Bond data
- Save Airbnb data ready for joining

**Output:**

- `3_airbnb_ready_for_join.csv`

### 4. `4_analyse.py`

**Purpose:** Join Airbnb and Bond data and calculate the rental-price gap.

**Main steps:**

- Check required Airbnb and Bond columns
- Make sure the join columns use matching data types before joining Airbnb and Bond data
- Filter Bond data to overall rental summaries: `Dwelling Type = ALL` and `Number Of Beds = ALL`
- Check that each Bond `Location Id + TimeFrame` combination is unique
- Inner join Airbnb and Bond using `SA2 location` and `TimeFrame`
- Convert weekly Bond rent to a daily equivalent
- Calculate the rental gap
- Calculate the median rental gap for each Airbnb month

**Calculations:**

- Long-term daily rent = Median Rent / 7

- Rental gap = Airbnb nightly price - Long-term daily rent

A positive rental gap means the Airbnb nightly price is higher than the daily equivalent of the long-term rent.

**Outputs:**

- `4_airbnb_bond_joined.csv`
- `4_rental_gap_by_time.csv`

### 5. `5_create_plots.py`

**Purpose:** Create the final visualisation.

**Main steps:**

- Read the monthly rental-gap results
- Create a line plot of the median rental gap over time
- Save the plot

**Output:**

- `5_rental_gap_over_time.png`

## Answer to the research question

The gap between Airbnb nightly prices and long-term daily rent was higher in **March–June 2026** than in **October–November 2025**. Within the available 2026 months, the gap decreased from March to May and then remained stable in June. This shows that the difference between short-term Airbnb prices and long-term daily-equivalent rent changed over time rather than remaining constant.

## Main limitations

- Airbnb and long-term residential rentals are different markets, so their prices are not directly equivalent.
- Bond `Median Rent` is weekly and is divided by 7 to create a daily equivalent for comparison with Airbnb nightly prices.
- Bond data is quarterly while Airbnb data is monthly.
- Airbnb price data is missing for December 2025, January 2026, and February 2026.
- July and August 2026 Airbnb data are successfully cleaned and processed, but they cannot be included in the final Airbnb–Bond comparison because the Bond dataset has no matching `2026-07-01` quarter.
- Linear regression was not used because there are only six usable monthly observations and there is a three-month data gap.

## Automation and orchestration

`run_pipeline.py` is the **orchestration file**.

It runs the five scripts in the correct order:
- 1_clean_new_airbnb.py
- 2_combine_airbnb.py
- 3_prepare_join.py
- 4_analyse.py
- 5_create_plots.py

The orchestration file uses:

- subprocess.run(..., check=True)

This means that if one stage fails, the pipeline stops instead of continuing with incorrect or incomplete data.

## Run the pipeline from the command line

Example using PowerShell:

- conda activate ds
- cd "path\to\deliverable_7"
- python run_pipeline.py

During Step 3, the pipeline asks for the Koordinates API key. The API key is entered when the pipeline runs and is not stored directly in the project files.

## Dependencies

### External packages

- **Python 3.12.13** — runs all pipeline scripts
- **pandas** — reads, cleans, combines, joins, and summarises the data
- **matplotlib** — creates the final plot
- **requests** — sends requests to the Koordinates API

### Python standard library

- **getpass** — allows the Koordinates API key to be entered securely
- **ThreadPoolExecutor** — speeds up multiple Koordinates API requests
- **subprocess** — runs the five scripts from `run_pipeline.py`
- **sys** — makes sure the pipeline uses the same Python environment

### Other requirement

- **Koordinates API key** — gives access to SA2 location data

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