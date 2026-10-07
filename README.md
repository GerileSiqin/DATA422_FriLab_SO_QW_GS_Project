# DATA422_FriLab_SO_QW_GS_Project

DATA422 group project repository for Friday lab

## What we have done so far

1. Created the GitHub repository: DATA422_FriLab_SO_QW_GS_Project.
2. Invited team members and tutors to the repository.
3. Added README.md, .gitignore, and requirements.R.
4. Set up the R + RStudio working environment.
5. Created the Trello board and invited team members.
6. Created a Data Wrangling WhatsApp group for communication.

## Next steps for Deliverable 1

1. Clone the repository onto each team member's computer.
2. Create and edit a simple test file.
3. Practise pull, commit, and push on the main branch.
4. Practise creating branches and pushing to branches.
5. Merge branches back into main.



### How to clone the repository

1. Open our GitHub repository: **DATA422_FriLab_SO_QW_GS_Project.**
2. Click the green **Code** button.
3. Copy the HTTPS link.
4. Open VS Code.
5. Press `Ctrl + Shift + P`.
6. Search for `Git: Clone`.
7. Paste the repository link.
8. Choose a folder on your computer.
9. Click **Open** or **Open in New Window** when VS Code asks.

After cloning, you should see these files:

- README.md
- .gitignore
- requirements.R
- team_guide.md
- DATA422_FriLab_SO_QW_GS_Project.Rproj



## Dataset information

For Deliverable 2, we use the `listings.csv` dataset from Inside Airbnb.

Dataset details:

- Source: Inside Airbnb
- File: `listings.csv`
- Location: New Zealand
- Month: June 2026
- Storage: Stored locally on each team member's computer

The dataset contains information about Airbnb listings in New Zealand.
Each row represents one Airbnb listing.
Each column describes one feature of that listing.

Important columns:

- `id`: unique identifier for each Airbnb listing
- `name`: name of the listing
- `host_id`: unique identifier for the host
- `host_name`: name of the host
- `neighborhood_group`: larger area or district, such as Christchurch
- `neighborhood`: smaller local area of the listing
- `latitude`: north-south coordinate of the listing location
- `longitude`: east-west coordinate of the listing location
- `room_type`: type of accommodation, such as entire apartment or private room
- `price`: price per night stayed
- `minimum_nights`: minimum number of nights required for booking
- `number_of_reviews`: total number of reviews for the listing
- `last_review`: date of the most recent review
- `reviews_per_month`: average number of reviews per month
- `calculated_host_listings_count` -> number of listings associated with the same host
- `availability_365`: number of days the listing is available in the next 365 days
- `number_of_reviews_ltm`: number of reviews in the last twelve months
- `license`: licence or registration information, if available

Note: Column meanings were interpreted using the Inside Airbnb Data Dictionary.

## Project organisation update

The repository has been organised into separate folders for each deliverable to make the project easier to navigate.

### Current folder structure

```text
deliverable_1/
  team_guide.md
  qi_git_practice.md

deliverable_2/
  Airbnb-Christchurch-NZ.ows
  Project-Progress.md
  brave_price_plot.R
```

The main project files remain in the root folder:

```text
README.md
.gitignore
requirements.R
```



### What changed

Deliverable 1 practice files were moved into the `deliverable_1/` folder.

Deliverable 2 workflow and support files were moved into the `deliverable_2/` folder.

The Airbnb dataset file `listings.csv` should still be stored locally on each team member's computer and should not be uploaded to GitHub.

### How to update your local repository

If you already cloned the repository to your computer, you do not need to clone it again.

Open the project folder in RStudio and run these commands in the RStudio Terminal:

```bash
git checkout main
git pull origin main
```

After pulling, your local repository should also show the new folders:

```text
deliverable_1/
deliverable_2/
deliverable_3/
```

## Git Guide for Team Members

Please follow this guide to avoid merge conflicts and accidentally overwriting another teammate’s work.

---

### 1. Why do merge conflicts happen?

A merge conflict can happen when:

- Two people edit the same lines in the same file.
- Several people work directly on the `main` branch.
- Someone starts working without downloading the latest changes.
- A teammate pushes new commits while you are still working.
- Both versions are accepted during a merge, creating duplicated code.

> The best solution is for every teammate to work on a separate branch.

---

### 2. Before starting work

First, make sure your local `main` branch is up to date:

```bash
git switch main
git pull --ff-only origin main

# DATA422 Deliverable 5 — Airbnb and tenancy bond integration

This folder reproduces the Stats NZ SA2 lookup, Airbnb enrichment, quarterly bond join, analysis, plots, and SQLite database.

## Data and API choices

- Stats NZ layer: [Statistical Area 2 2026](https://datafinder.stats.govt.nz/layer/123515-statistical-area-2-2026/)
- Koordinates layer ID: **123515**
- Query endpoint: `https://koordinates.com/services/query/v1/vector.json`
- Area fields: `SA22026_V1_00` and `SA22026_V1_00_NAME`
- Geographic areas reference: [Geographic Areas Table 2023](https://datafinder.stats.govt.nz/table/111243-geographic-areas-table-2023/)

## Run in the VS Code terminal

From the repository root:

```bash
source .venv/bin/activate
export KOORDINATES_API_KEY="your_key_here"
python Deliverable_5/01_test_koordinates_query.py
python Deliverable_5/run_deliverable_5.py --workers 8
```

The batch uses threads because the workload is network I/O, not CPU computation. This provides concurrent queries without the process-creation overhead of multiprocessing. The cache makes the run restartable.

## Outputs

- `data_processed/christchurch_airbnb_with_sa2.csv`: Airbnb data with SA2 code/name
- `data_processed/bond_location_quarter_totals.csv`: one bond total per SA2-quarter
- `data_processed/airbnb_bond_joined.csv`: left-joined analytical dataset
- `deliverable_5.sqlite`: prepared data and SQL-joined table
- `results/location_comparison.csv`: counts, rents, prices, and gaps by SA2
- `results/largest_gap_locations.csv`: top gap locations with at least five listings
- `results/data_quality_summary.json`: enrichment/join coverage checks
- `results/analysis_summary.md`: written answers and assumptions
- `results/plots/`: analysis plots

## Trello reflection prompt

Update the team board with completed cards for API validation, SA2 enrichment, the time/location join, SQLite, quality checks, and GitHub publication. In the reflection, discuss the benefit of testing one query first, using a resumable cache, choosing the correct quarterly grain, and avoiding double counting in the bond breakdowns. Add remaining review/presentation work as named cards with owners and due dates.

**Active long-term bonds** are the number of active tenancy bonds recorded for long-term rentals in an area. In New Zealand, a bond is money lodged with Tenancy Services when a tenant rents a property. Here, `Active Bonds` is used as the closest available proxy for the number of long-term rental properties.

**Airbnb listings** are the short-term accommodation listings found in the Airbnb snapshot. They may represent entire homes, apartments, or individual rooms.

**Why compare them?**

# Deliverable 4

## Choose a local input file

Run either cleaning script from the project root in a terminal:

```bash
python deliverable_4/clean_bond.py
python deliverable_4/clean_listings.py
```

Each script asks for an input path before reading data. Paste the full path to
your CSV file, or enter its folder path to use the default filename in that
folder. Press Enter to use the displayed default, or type `q` to cancel.
Invalid paths prompt you to try again. Paths containing spaces, surrounding
quotes, and `~` for your home directory are supported.

This is a terminal text prompt, not a separate graphical window. In VS Code,
use **Run Python File in Terminal** so you can type a response.

The listings input must have the same columns as the combined Christchurch
dataset from Deliverable 3 (`christchurch_airbnb_cleaned.csv`). The bond input
must use the expected rental bond CSV structure. Choosing a file changes its
location only; it does not change the cleaning rules or expected columns.
Cleaned outputs are still saved under `deliverable_4/data_processed` and
`deliverable_4/bond_data_processed`, respectively.

## Christchurch Airbnb Dataset

The Christchurch Airbnb dataset originally contained **28795 rows and 19 columns** and covered the period from **October 2025 to June 2026**.

### Cleaning script

The initial inspection and cleaning code is in:

`clean_listings.py`

The script currently:

- reads the Christchurch Airbnb dataset
- inspects rows, columns, data types, and missing values
- checks for duplicate rows
- checks latitude and longitude
- investigates important columns
- investigates missing price patterns
- investigates unusually high price values

### Cleaning decisions

| Cleaning decision | Reason | Consequence |

|---|---|---|

| Checked for exact duplicate rows and removed duplicates if found | Duplicate rows could cause listings to be counted more than once | No exact duplicate rows were found, so **0 rows were removed** |

| Kept `latitude` and `longitude` | These columns are required for Deliverable 4 and may be useful for location-based analysis | Both columns had no missing values, so **0 rows were removed** |

| Removed `license` | All 28795 values were missing, so the column contained no usable information | **1 column removed**, 0 rows removed |

| Removed `neighbourhood_group` | Every row contained the same value, `Christchurch City`, so the column did not provide additional information | **1 column removed**, 0 rows removed |

| Removed `name`, `host_id` and `host_name` | These columns are not required for the planned comparison of rental prices and property availability | **3 columns removed**, 0 rows removed |

| Removed `number_of_reviews`, `last_review`, `reviews_per_month` and `number_of_reviews_ltm` | Review-related information is not required for the planned analysis of rental prices and available properties | **4 columns removed**, 0 rows removed |

| Kept missing `price` values | There were **10667 missing price values**. All listings in December 2025, January 2026 and February 2026 had missing prices. Removing these rows would remove three complete months and affect later analysis of property availability | **10667 missing values retained**, 0 rows removed |

| Kept missing `minimum_nights` values | Only **37 values** were missing and `minimum_nights` is not essential for the planned comparison of rental prices and property availability | **37 missing values retained**, 0 rows removed |

| Kept unusually high `price` values | The highest prices were inspected by sorting the dataset by `price` and reviewing the associated listing names and IDs. Although some prices were extremely high, they were associated with identifiable listings and there was insufficient evidence to classify them as data-entry errors. | **0 rows removed** |

| Kept `id`, `neighbourhood`, `latitude`, `longitude`, `room_type`, `price`, `minimum_nights`, `calculated_host_listings_count`, `availability_365` and `month_year` | These columns are useful for identifying listings, comparing locations, analysing prices and examining property availability over time | Final dataset contains **10 columns** |

### Cleaning outcome

- Original dataset: **28795 rows and 19 columns**
- Final dataset: **28795 rows and 10 columns**
- Rows removed: **0**
- Columns removed: **9**
- Exact duplicate rows removed: **0**
- Missing `price` values retained: **10667** 
- Missing price values were retained because three complete months had no price data.
- Missing `minimum_nights` values retained: **37**

The cleaning process was designed to preserve the information needed for the next stage of the project, where the Airbnb data will be combined with rental bond data to compare **rental prices** and **property availability** over the same time period.

---

## Rental Bond Dataset

### Source

Downloaded from **Tenancy Services, New Zealand**.

Dataset used:

`Detailed quarterly report, January 2020 to April 2026`

Local filename:

`bond_data_jan2020_apr2026.csv`

The dataset provides information about New Zealand’s private rental market. It is based on rental bonds for new tenancies that private landlords submit to Tenancy Services.

The data is organised by **tenancy start date** (i.e. the date the rental agreement begins) and uses **SA2-2019 geographic area definitions** from Statistics New Zealand.

To protect privacy, bond counts are slightly rounded, and very small counts are not published.

The data is currently in a **provisional state** because Tenancy Services is migrating to a new bond management system. Recent figures may therefore be incomplete, revised, or affected by system and methodology changes.

### Column descriptions

A separate data dictionary was not found on the Tenancy Services webpage.

The following fields must be retained for Deliverable 4:

- `Location Id`
- `TimeFrame`

Additional column descriptions will be added after inspecting the downloaded dataset.

### Cleaning decisions

| Cleaning decision | Reason | Consequence |

|---|---|---|

| Filtered the dataset to `2025-10-01`, `2026-01-01`, and `2026-04-01` | These three quarterly periods cover the same overall period as the Christchurch Airbnb dataset, from October 2025 to June 2026 | Rows outside the target period were removed: **198868 rows** |

| Kept `TimeFrame` | This field is required for Deliverable 4 and is needed to compare the bond data over time | Column retained |

| Kept `Location Id` | This field is required for Deliverable 4 and it shows which quarter each row belongs to and is needed to compare the data across the three quarters | Column kept |

| Removed rows with missing `Location Id` | `Location Id` is needed to identify the geographic area of each row. Without it, the row cannot be confidently matched to the correct area in the Airbnb dataset | Rows with missing `Location Id` were removed: **94 rows** |

| Kept missing `Number Of Beds` values | Some dwelling types have missing `Number Of Beds` values repeatedly, suggesting that the bedroom number was not recorded for those categories rather than being accidentally missed | Missing values were kept: **876 values** |

| Kept missing `Median Rent` values | Some values may be intentionally hidden for privacy. Replacing them would require guessing, and removing the rows would also discard other useful data | Missing `Median Rent` values were kept. After filtering and removing rows with missing `Location Id`, **0 missing `Median Rent` values remained** |

| Kept all 12 columns | All columns may still be useful for later comparison of rental prices and rental market activity | No columns were removed at this stage |

| Checked for exact duplicate rows | If the same row appears more than once, the same data could be counted more than once and lead to incorrect totals or misleading results | No exact duplicate rows were found: **0 rows removed** |

### Cleaning outcome

- Original dataset: **226080 rows and 12 columns**
- Rows remaining after filtering to the three selected quarters:: **27212**
- Rows removed outside the target period: **198868**
- Rows removed because `Location Id` was missing: **94**
- Final cleaned dataset: **27118 rows and 12 columns**
- Exact duplicate rows removed: **0**
- Missing `Number Of Beds` values retained: **876**
- Missing `Median Rent` values remaining: **0**
- Columns removed: **0**

The final cleaned dataset contains only the three quarterly periods that match the Airbnb dataset and retains the information needed for later comparison of rental prices and rental market activity.

Quote from Tenancy Services (https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/)
Important:
Rental bond data migration to the new bond management system continues and therefore data remains in a provisional state at this time. Data is sourced from both legacy and new systems and may be incomplete or revised.

Reported figures may reflect system changes, data reclassification, and methodology updates rather than underlying trends. Recent data may not be directly comparable with earlier periods. There are 17,550 more active bonds because the two systems recorded the information differently. We are undertaking further data validation, clean-up, and methodology refinement to ensure consistency and accuracy of reporting going forward.

Users should exercise caution when comparing recent data releases with earlier periods, as these may not be directly comparable due to the impacts of migration and ongoing data normalisation. We will provide further information as this work continues.

# DATA422 Deliverable 5 — Airbnb and tenancy bond integration
The figure places both measures side by side by Statistical Area 2 to compare:

- the scale of short-term accommodation activity; and
- the scale of the conventional long-term rental market.

It helps identify locations where Airbnb listings are especially concentrated relative to long-term rentals.

**What the figure shows**

- Yellow bars: active long-term tenancy bonds.
- Blue bars: Airbnb listings.
- The figure displays the 20 locations with the most Airbnb listings.
- A much larger yellow bar means the area has many more long-term rentals than Airbnb listings.
- A relatively large blue bar means Airbnb activity is substantial compared with the local long-term rental market.

The figure is useful for showing geographic patterns, but it does **not** prove that Airbnb listings cause fewer long-term rentals. The measures have different definitions: one bond does not necessarily equal one unique property, and one Airbnb listing may be a room or an entire property. Also, some areas have no matched bond data, so missing yellow bars should not automatically be interpreted as zero rentals.

```text
Raw Airbnb data
    │
    │ clean
    ▼
Clean Airbnb data
(latitude, longitude, price, time...)
    │
    │ Koordinates API
    ▼
Add Stats NZ area/location ID
    │
    ▼
Enriched Airbnb data
(area_id, price, time...)
    │
    │
    │ JOIN on:
    │ area_id + time
    │
    ├───────────────────────┐
    │                       │
    ▼                       ▼
Airbnb data            Bond/rental data
(short-term)           (long-term)
    │                       │
    └──────────┬────────────┘
               ▼
        Combined dataset
               │
               ▼
        Compare rental markets
               │
        ┌──────┼───────────┐
        ▼      ▼           ▼
     Median   Price       Number of
     price    gaps        properties
```

# DATA422 Deliverable 6

This folder contains a reviewed and executed revision of the Deliverable 5 comparison pipeline, high-level change notes, a sanity-check demonstration, and AI-assisted design principles. Earlier deliverables and the supplied `example-automated-pipeline.zip` remain unchanged.

## Start with the documents

- `docs/Design_Principles.docx`: editable Word document covering the four required areas and identifying OpenAI ChatGPT through Codex as the AI used.
- `docs/Coding_Review_and_Sanity_Check.docx`: high-level changes and reasons, intentional result changes, and a worked sanity check for the tutor.
- Equivalent Markdown versions are stored alongside them.

## Inputs and scope

The default inputs are `../deliverable_3/data_processed/christchurch_airbnb_cleaned.csv` and `../deliverable_4/bond_data_processed/bond_data_clean_qi.csv`. The Airbnb input retains `snapshot_date`, which the narrower Deliverable 4 Qi listing file drops. The revised pipeline validates prepared data and reproduces enrichment, joining, analysis and export; it does not rebuild the previous raw-data cleaning stages.

`inputs/koordinates_coordinate_cache.csv` is a byte-preserved copy of the existing Deliverable 5 cache. Offline mode is the default and needs no API key. `inputs/source_materials_manifest.json` records the reviewed input and reference fingerprints. The supplied lecture supports modularity, descriptive functions, explicit data flow, project-relative paths and scripted changes. The supplied automated-pipeline ZIP demonstrates staged automation, configuration and inspectable outputs.

## Reproduce

Use Python 3.14 and an environment with the versions in `requirements.txt` (the actual analysis versions are also recorded in `results/run_manifest.json`). The document builder additionally needs `python-docx`.

From this folder:

```sh
python3 -m pip install -r requirements.txt
make
```

For an existing environment, set `make PYTHON=/path/to/python`. If document generation uses a separate environment, set `DOCUMENT_PYTHON=/path/to/document/python`. `make` runs the full analysis, saved-output sanity demonstration, regression and edge-test verification, and Word and Markdown document generation. It deliberately rebuilds the workflow; it does not implement per-stage incremental builds. R and Quarto are unnecessary for this Python implementation.

Run individual stages:

```sh
python3 run_pipeline.py
python3 sanity_check_example.py
python3 -m unittest discover -s tests -v
python3 tools/verify_delivery.py
python3 tools/build_documents.py
```

For different inputs:

```sh
python3 run_pipeline.py --airbnb /path/listings.csv --bonds /path/bonds.csv \
  --cache /path/cache.csv --output /path/new_results
```

Only the pipeline and sanity script support alternative result directories. The delivered document builder and regression verifier intentionally use this folder's `results` and the supplied June 2026 baseline; they need adapting before being used as verification of another dataset. One snapshot per quarter is required. `config.json` changes worker count and the observed-gap minimum; both also have command-line overrides.

New SA2 queries require `--allow-network` and `KOORDINATES_API_KEY` in the environment. The current package was verified offline. A failed live run retains its checkpoint; resume by passing that checkpoint as `--cache` and selecting a new `--output` folder. Input files cannot be located inside the selected output folder.

## Verified results and intentional corrections

- 3,469 listings retained; 3,469 SA2 matches; 2,673 bond records and rents matched; 2,474 usable listing gaps; 274 missing prices retained.
- 174 SA2 groups. All prior joined values and location statistics match Deliverable 5 within numeric tolerance.
- 10 analytical checks and 19 adversarial tests passed; all six SQLite tables match their CSV contents.
- Gap ranking now requires five **observed price gaps**, rather than five total listings. Four locations leave the eligible set (95 to 91), including the previous leader Bryndwr South, which has only four priced listings.
- Wigram North and Holmwood share the highest eligible gap rounded to cents, NZ$242.71. Christchurch Central remains NZ$250.00 median/night, from 117 priced listings among 119 total listings.

## Package map

`run_pipeline.py` orchestrates the stages in `pipeline/`. `tests/` contains edge tests. `sanity_check_example.py` verifies saved outputs and hand-checks one listing. `tools/verify_delivery.py` independently checks exports and baseline agreement. `tools/build_documents.py` generates the Word and Markdown documents from verified evidence.

`results/data_processed/` contains six CSV tables; `results/deliverable_6.sqlite` contains the same tables. Plots, automatically generated analysis notes, quality checks, a run manifest, the persisted sanity example, the test log and delivery verification report are in `results/`. `_SUCCESS.json` marks successful completion of the analytical pipeline, not of document rendering or every later verification stage.

The geographic cache is inherited evidence, not a fresh API or polygon check. Bond SA2 vintage compatibility is unresolved from the available files. Active bonds and Airbnb listings have different definitions; missing bond data is not zero. The reported price gap is descriptive and does not establish causation or returns.
