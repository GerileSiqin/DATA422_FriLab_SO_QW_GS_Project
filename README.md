
# DATA422 — Data Wrangling Group Project

**University of Canterbury | Friday Lab**

## 1. Project overview

This repository contains our group work for DATA422 Data Wrangling for Data Science.

Throughout the course, we developed our data wrangling skills by exploring, cleaning, transforming, combining and analysing real-world datasets using Orange Data Mining, Python and GitHub.

Our work focused on Airbnb listings in New Zealand, particularly Christchurch, and long-term rental bond data from Tenancy Services.

The project developed through seven deliverables:

1. Set up GitHub and establish team collaboration.
2. Explore Airbnb data using Orange Data Mining.
3. Use Python to prepare, combine and analyse monthly Airbnb datasets.
4. Clean Airbnb and rental bond datasets and document cleaning decisions.
5. Integrate the two datasets using geographical area codes and time periods, and perform comparative analyses.
6. Review coding practices, improve the workflow and verify results.
7. Automate the data wrangling pipeline and incorporate July and August 2026 Airbnb data.

The overall development progressed from manual data exploration towards a more structured, reproducible and automated workflow.

The repository preserves the work completed at each stage, including code, documentation, results and team contributions.

## 2. Tools and dependencies

Our group used the following tools and technologies.

### 2.1 Software and non-code tools

| Tool | Purpose |
|---|---|
| Orange Data Mining | No-code data exploration, filtering, transformation and visualisation |
| Visual Studio Code | Writing, running and debugging Python scripts |
| Python | Data cleaning, transformation, integration, analysis and automation |
| Git and GitHub | Version control, collaboration and repository management |
| Trello | Project management and tracking group progress |
| Koordinates API | Obtaining geographical area codes from latitude and longitude |
| SQLite | Storing and joining prepared datasets in Deliverable 5 and related work |

### 2.2 External Python packages

These packages need to be installed in the Python environment used by the relevant scripts.

| Package | Purpose |
|---|---|
| `pandas` | Reading CSV files, inspecting datasets, cleaning, filtering, grouping, merging and calculating summary statistics |
| `matplotlib` | Creating histograms, line plots and other visualisations |
| `requests` | Sending API requests to Koordinates for geographical mapping |

Some deliverables have additional dependencies. Refer to their own requirements files and documentation for the relevant setup.

### 2.3 Python standard library modules

The project also uses Python's built-in modules, which do not require separate installation.

| Module | Purpose |
|---|---|
| `subprocess` | Running multiple scripts in sequence for pipeline automation |
| `sys` | Accessing the Python interpreter and execution environment |
| `concurrent.futures` | Using `ThreadPoolExecutor` to process multiple API requests concurrently |
| `pathlib` | Managing file and directory paths |
| `sqlite3` | Working with SQLite databases |
| `json` | Reading and writing structured configuration or verification information |

Not every module is used in every deliverable.

## 3. Input datasets

The project uses several datasets from different sources and time periods.

### 3.1 Airbnb listings

**Source:** [Inside Airbnb](https://insideairbnb.com/get-the-data/)

The Airbnb datasets contain information about accommodation listings, including:

- Listing ID and location
- Latitude and longitude
- Room type
- Nightly price
- Minimum nights
- Reviews and review dates
- Availability information

The project initially explored the June 2026 New Zealand dataset.

In Deliverable 3, the work was extended to monthly Airbnb snapshots covering October 2025 to June 2026, with a focus on Christchurch City.

In Deliverable 7, new Airbnb datasets for July and August 2026 were added to update the analysis.

The original datasets are large and are generally stored locally rather than committed to GitHub.

### 3.2 Long-term rental bond data

**Source:** [Tenancy Services New Zealand](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/)

The rental bond dataset contains information about New Zealand's long-term residential rental market.

Important fields include:

- `Location Id`
- `Location Name`
- `TimeFrame`
- `Median Rent`
- `Dwelling Type`
- `Number Of Beds`
- Rental bond activity and counts

The original dataset contains records from 2020 to April 2026.

For the cleaning and integration work, the data was filtered to three quarterly periods:

- 2025-10-01
- 2026-01-01
- 2026-04-01

These periods were selected to align with the earlier Airbnb datasets.

### 3.3 Geographic area data

**Source:** [Stats NZ Statistical Area 2 data via Koordinates](https://datafinder.stats.govt.nz/layer/123515-statistical-area-2-2026/)

The Airbnb datasets contain latitude and longitude, while the rental bond dataset uses geographical location identifiers.

The Koordinates API was used to obtain Statistical Area 2 (SA2) codes and names for Airbnb listings.

This geographical mapping made it possible to connect Airbnb records with rental bond data by location.

## 4. Data processing and transformation

The data wrangling work was developed and improved across the deliverables.

### 4.1 Data exploration

We first used Orange Data Mining to explore the Airbnb dataset without writing the full workflow in Python.

The exploration included:

- Inspecting variables and data distributions
- Filtering listings by geographical area
- Comparing price distributions
- Calculating days since the last review
- Identifying highly reviewed listings

These activities helped us understand the dataset and identify suitable analyses.

### 4.2 Preparing monthly Airbnb data

In Deliverable 3, Python was used to:

1. Read monthly Airbnb datasets.
2. Filter the data to Christchurch City.
3. Add month and year information.
4. Combine records from different monthly snapshots.
5. Inspect summary statistics and missing values.
6. Save processed datasets for later work.

This introduced a more systematic and code-based approach to data preparation.

### 4.3 Cleaning Airbnb and rental bond data

In Deliverable 4, we inspected the datasets and made cleaning decisions based on the requirements of later analyses.

The cleaning activities included:

- Checking data types and required columns
- Identifying missing values
- Checking duplicate records
- Inspecting price distributions and unusually high values
- Retaining essential geographical information
- Filtering rental bond data to relevant quarterly periods
- Removing records without required location identifiers
- Saving cleaned datasets

The cleaning decisions and their consequences were documented.

**Important:** The Deliverable 4 documentation includes different Airbnb inputs. An earlier analysis describes a nine-month dataset containing 28,795 rows, while a later verified cleaning run used a June 2026 dataset containing 3,469 rows. These are different processing scopes, and their results should not be treated as identical.

### 4.4 Geographical mapping and data integration

In Deliverable 5, we used the Koordinates API to map Airbnb latitude and longitude coordinates to SA2 geographical areas.

The main processing stages were:

1. Obtain SA2 area identifiers for Airbnb listings.
2. Add geographical identifiers to Airbnb data.
3. Prepare compatible time fields.
4. Match Airbnb records with the relevant rental bond summaries.
5. Calculate rental-price comparisons.
6. Produce analytical tables and plots.

The project also explored the use of SQLite for storing prepared data and performing joins.

### 4.5 Improving and verifying the workflow

In Deliverable 6, we reviewed the existing pipeline and considered coding best practices.

The work included:

- Reviewing code structure and readability
- Documenting improvements and their reasons
- Describing pipeline inputs, outputs and stages
- Demonstrating sanity checks
- Checking analytical outputs and data consistency
- Documenting design principles

This stage focused on improving reliability, transparency and reproducibility rather than introducing an entirely new research question.

### 4.6 Automation

In Deliverable 7, the workflow was organised into five scripts controlled by one orchestration file, `run_pipeline.py`.

The scripts run in the following order:

| Order | Script | Main function |
|---|---|---|
| 1 | `1_clean_new_airbnb.py` | Clean July and August Airbnb data |
| 2 | `2_combine_airbnb.py` | Combine new and previous Airbnb data |
| 3 | `3_prepare_join.py` | Add SA2 location information and prepare time fields |
| 4 | `4_analyse.py` | Perform monthly Airbnb analysis and matched rental-gap analysis |
| 5 | `5_create_plots.py` | Generate updated visualisations |

The orchestration file uses `subprocess.run(..., check=True)`, so the pipeline stops if a stage fails.

This allows the processing and analysis to be updated through one command.

## 5. Processed datasets and outputs

Different deliverables produce different processed datasets, analytical results and supporting files.

The main outputs include:

| Deliverable | Output | Purpose |
|---|---|---|
| 2 | Orange workflow and reports | Record the initial no-code exploration |
| 3 | Combined Christchurch Airbnb dataset | Prepare monthly Airbnb records for later analysis |
| 4 | `christchurch_listings_clean.csv` | Store cleaned Airbnb listings for the selected input |
| 4 | `bond_data_clean.csv` | Store cleaned quarterly rental bond data |
| 5 | Airbnb dataset with SA2 identifiers | Connect Airbnb coordinates to geographical areas |
| 5 | Joined Airbnb–Bond dataset | Support location and rental-price comparisons |
| 5 | SQLite database and analysis results | Store and analyse integrated information |
| 6 | Revised pipeline results and verification records | Document checks, improvements and reproducibility |
| 7 | `2_airbnb_combined.csv` | Combine previous and new Airbnb data |
| 7 | `3_airbnb_ready_for_join.csv` | Prepare geographical and time fields |
| 7 | `4_airbnb_price_by_time.csv` | Store monthly Airbnb price summaries |
| 7 | `4_airbnb_bond_joined.csv` | Store matched Airbnb–Bond observations |
| 7 | `4_rental_gap_by_time.csv` | Store monthly rental-gap summaries |
| 7 | `5_airbnb_price_over_time.png` | Visualise Airbnb median prices |
| 7 | `5_rental_gap_over_time.png` | Visualise rental-price gaps over time |

Some datasets are generated locally and may not be committed to GitHub because of their size.

The relevant deliverable folders contain the available scripts, outputs and documentation.

## 6. Analyses completed and main findings

Different deliverables addressed different analytical tasks. The following sections summarise the main outcomes.

### 6.1 Initial Airbnb exploration — Deliverable 2

The Orange Data Mining workflow examined Airbnb price distributions, review activity and geographical differences.

The analysis included:

- Price histograms for New Zealand and Christchurch City
- Distribution of days since the last review
- Identification of listings in the most-reviewed 10% nationally

The analysis found **343 Christchurch City listings** among the most-reviewed 10% of New Zealand listings in the dataset used.

This stage demonstrated how filtering, transformations and visualisation can be combined into a no-code workflow.

### 6.2 Airbnb dataset preparation and cleaning — Deliverables 3–4

The Airbnb data was prepared for later geographical and rental comparisons.

For the earlier nine-month Christchurch dataset, the documented inspection reported:

- 28,795 rows
- 19 columns before cleaning
- 10,667 missing price values
- Missing price data across December 2025, January 2026 and February 2026

The later verified June 2026 cleaning run retained 3,469 records and 14 columns.

For the rental bond dataset:

- Original records: 226,080
- Records after selecting three quarters: 27,212
- Records removed due to missing location identifiers: 94
- Final cleaned records: 27,118

These checks helped establish which records and variables could be used in later analyses.

### 6.3 Geographical and rental-price comparisons — Deliverable 5

The Airbnb and bond datasets were integrated using geographical area identifiers and compatible time periods.

The analysis examined:

- Median Airbnb nightly prices by location
- Differences between Airbnb nightly prices and daily-equivalent long-term rent
- Locations with relatively large rental-price gaps
- Airbnb listing counts compared with rental bond activity

The documented Christchurch Central median Airbnb nightly price was **NZ$250** for the earlier analysed snapshot.

Geographical comparisons showed that Airbnb activity and long-term rental activity vary across Christchurch areas.

However, the measures describe different markets, so differences should not be interpreted as proof that Airbnb activity reduces long-term rental availability.

### 6.4 Coding improvements and verification — Deliverable 6

The existing analysis workflow was reviewed and tested.

The Deliverable 6 documentation reports successful checks of data processing, joins, saved outputs and analytical results.

One important improvement was to require at least five observed rental-price gaps when ranking locations, rather than five total listings.

This reduced the risk of ranking locations based on too few usable price observations.

The work also demonstrated the value of sanity checking, modular code and documenting assumptions.

### 6.5 Rental-gap trend — Deliverable 7

The final automated pipeline calculated the difference between Airbnb nightly prices and the daily equivalent of long-term median weekly rent.

The calculation was:

```text
Long-term daily rent = Median Rent / 7

Rental gap = Airbnb nightly price - Long-term daily rent
```

The analysis found that:

- The median rental gap was higher in March–June 2026 than in October–November 2025.
- Within the available 2026 months, the gap decreased from March to May.
- The gap remained broadly stable in June.

This indicates that the observed rental-price difference changed over the available time periods rather than remaining constant.

### 6.6 Updated Airbnb price analysis — Deliverable 7

The July and August 2026 Airbnb datasets were added to the automated pipeline.

Because matching Q3 2026 bond data was unavailable, these months were included in the Airbnb-only price analysis rather than the Airbnb–Bond rental-gap analysis.

The updated results were:

| Location | July 2026 | August 2026 |
|---|---:|---:|
| Christchurch overall | NZ$227 | NZ$224 |
| Christchurch Central | NZ$253 | NZ$256 |

These figures represent median Airbnb nightly prices.

The results show that Christchurch Central had a higher median nightly price than Christchurch overall in both months.

Between July and August, the median price decreased slightly for Christchurch overall but increased slightly for Christchurch Central.

## 7. Main limitations

The project has several important data and methodological limitations.

### Missing data

Airbnb prices were unavailable for December 2025, January 2026 and February 2026 in the data used for the rental-gap analysis.

These missing months prevent a complete continuous monthly comparison.

### Different time periods

Airbnb observations are monthly, while rental bond data is quarterly.

The datasets must therefore be aligned before joining.

The available bond data does not contain the Q3 2026 quarter, so July and August 2026 cannot be included in the rental-gap analysis.

### Different rental markets

Airbnb nightly prices and long-term residential rents are not directly equivalent.

Dividing weekly median rent by seven provides a daily comparison measure, but it does not account for differences in occupancy, operating expenses, property type or rental arrangements.

### Geographic matching

The analysis depends on matching Airbnb coordinates to SA2 geographical identifiers and corresponding rental bond records.

Differences between geographic definitions or missing matches can affect the comparison.

### Rental bond data quality

The rental bond data may be provisional due to changes in the bond management and reporting systems.

Reported differences may therefore partly reflect revisions or methodological changes.

### Interpretation of results

The analyses are descriptive and do not establish causal relationships between Airbnb activity and long-term rental prices or availability.

For the rental-gap trend, linear regression was not used because there were only six usable monthly observations and a three-month gap in the series.

## 8. Repository organisation

The repository is organised by deliverable.

| Folder | Contents |
|---|---|
| [`deliverable_1/`](deliverable_1/) | Git practice and team collaboration |
| [`deliverable_2/`](deliverable_2/) | Orange workflows and initial Airbnb exploration |
| [`deliverable_3/`](deliverable_3/) | Monthly Airbnb data preparation and exploration |
| [`deliverable_4/`](deliverable_4/) | Cleaning scripts and supporting documentation |
| [`deliverable_5/`](deliverable_5/) | Geographic mapping, dataset integration and analysis |
| [`deliverable_6/`](deliverable_6/) | Coding review, design principles, tests and verification |
| [`deliverable_7/`](deliverable_7/) | Automated pipeline and updated analyses |

Each deliverable preserves the work from that stage of the course.

## 9. Running the final automated pipeline

The final automated workflow is located in `deliverable_7/`.

It requires Python, the necessary external packages, four input datasets and a Koordinates API key.

From the Deliverable 7 directory, run:

```powershell
python run_pipeline.py
```

The five scripts are then executed in order.

For the environment used during development, the following commands were used:

```powershell
conda activate ds
cd "path\to\deliverable_7"
python run_pipeline.py
```

The API key is read from a local `api_key.txt` file. This file must not be committed to GitHub.

For detailed input requirements, processing steps, dependencies and outputs, refer to the Deliverable 7 README.

## 10. Team collaboration

The project was developed collaboratively using GitHub, branches, commits and pull requests.

We also used Trello to manage project progress and a WhatsApp group for communication.

The Git history records the development of the project and provides evidence of contributions by team members.

## 11. Acknowledgements

We thank our DATA422 lecturers and tutors for their guidance and feedback throughout the course.

We also thank our teammates for their contributions and collaboration.

We acknowledge Inside Airbnb, Tenancy Services New Zealand, Stats NZ and Koordinates for providing the datasets and geographic information used in our project.

**Ngā mihi nui!**