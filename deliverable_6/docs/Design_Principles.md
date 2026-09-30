# Airbnb and tenancy bond pipeline design principles

DATA422 Deliverable 6  |  30 September 2026

The pipeline compares Christchurch Airbnb nightly prices and listing counts with quarterly tenancy bond statistics by Statistical Area 2. It preserves listing records, aligns dates to quarters, and makes the price comparison in consistent nightly units. The revised implementation is in deliverable_6 and reads the previously prepared files.

OpenAI ChatGPT through Codex was the AI used to assist with the code review, refactoring, tests and document drafting. The documents were reconciled with the implemented code and the executed verification results.

## 1 Inputs to the pipeline

### Christchurch Airbnb listings

The default input is deliverable_3/data_processed/christchurch_airbnb_cleaned.csv. Each row represents one listing in one snapshot. Required fields are id, latitude, longitude, price and snapshot_date. The current file has 3,469 rows and 23 columns, with snapshot_date 2026-06-19. The pipeline preserves the other input fields, including listing and host information.

The Deliverable 3 cleaning stage has already standardised fields, checked duplicate listing-month keys, handled impossible numeric values, selected Christchurch City and attached snapshot dates. Deliverable 6 validates that prepared input; it does not repeat raw-data acquisition or claim to rebuild the upstream cleaning stages.

### Quarterly tenancy bond statistics

The default input is deliverable_4/bond_data_processed/bond_data_clean_qi.csv, containing 26,991 rows and 12 columns for 2025-10-01, 2026-01-01 and 2026-04-01. These are national location-level records and category breakdowns. Required fields are TimeFrame, Location Id, Dwelling Type, Number Of Beds, Active Bonds, Total Bonds and Median Rent. The analysis selects published ALL/ALL totals, leaving 4,865 unique location-quarter rows.

### Geographic lookup and settings

inputs/koordinates_coordinate_cache.csv is a byte-preserved copy of the Deliverable 5 SA2 cache, with 3,171 coordinate pairs and five fields: longitude, latitude, area_code, area_name and query_status. Its recorded source is Koordinates layer 123515, Statistical Area 2 2026. config.json sets the worker count and observed-gap minimum. Command-line options select inputs, cache, output folder and network access. An API key is read only from KOORDINATES_API_KEY when new queries are needed.

## 2 Outputs from the pipeline

All generated analytical outputs go into deliverable_6/results by default. Earlier source files are read only. Intermediate tables make the transformations inspectable and support debugging.

- data_processed/airbnb_prepared.csv contains validated listing data and the derived bond_time quarter.

- data_processed/airbnb_enriched.csv adds SA2 code, name and query status to every listing.

- data_processed/bond_location_quarter.csv contains the ALL/ALL published totals at a unique location-quarter grain.

- data_processed/airbnb_bond_joined.csv adds bond statistics, a bond_row_matched flag, median_long_term_nightly_rent and nightly_price_gap.

- data_processed/location_comparison.csv reports listing counts, priced-listing counts, observed-gap counts, medians and active bond counts separately for each SA2-quarter.

- data_processed/largest_gap_locations.csv ranks up to 20 qualifying locations per quarter; plots show the 15 largest gaps and counts for the 20 areas with most listings.

- deliverable_6.sqlite stores the same six tables as the CSV exports. Missing values become SQL NULL; dates are stored as ISO text.

- koordinates_coordinate_cache.csv is the output checkpoint cache. analysis_summary.md and data_quality_summary.json are generated from the run. run_manifest.json records paths, hashes, settings and software versions. _SUCCESS.json marks a completed analytical run.

The verification and document stages add sanity_check_example.json, verification_report.json and test_results.txt. docs contains the design principles and tutor change notes in editable Word and Markdown formats. The document builder uses verified result files to keep counts and conclusions consistent.

### Observed output and interpretation

The executed June 2026 run retains 3,469 listings across 174 SA2 groups. All 3,469 listings have cached SA2 assignments. 2,673 listings match a bond total (77.1%); 2,474 have a usable price gap. The 274 missing Airbnb prices are retained.

Christchurch Central has 119 listings, of which 117 have prices; the median nightly price is NZ$250.00. Using at least 5 observed listing gaps, Wigram North, Holmwood share the highest gap rounded to cents, NZ$242.71. Exact numeric values determine sort order, with area code as the final tie-breaker.

The comparison is descriptive. Active bonds are a proxy for long-term rental activity, and Airbnb listings can include rooms as well as entire properties. Weekly rent divided by seven is a unit conversion, not evidence of equivalent accommodation quality, occupancy, returns or causal effects.

## 3 Main steps in the pipeline

### Validate prepared inputs

prepare_airbnb checks required columns, positive integer IDs, valid dates, numeric nonnegative observed prices and New Zealand coordinate bounds. Missing prices remain missing. It rejects duplicate id and snapshot_date keys and multiple snapshots in the same quarter to prevent repeated listings from affecting a quarter comparison. prepare_bonds validates the schema, selects ALL/ALL totals, checks quarter-start dates and rejects duplicate Location Id and TimeFrame keys.

### Attach SA2 geography

load_cache validates coordinate-key uniqueness and complete successful responses. enrich_coordinates performs a many-to-one coordinate join. Offline mode is the default and requires each input pair to have an ok or no_match result. Missing or failed pairs stop an offline run. With --allow-network, failed and missing pairs are queried after a single-query test, with bounded retries and concurrent workers. Input cache files are preserved and output cache checkpoints are saved atomically.

### Align time and join bond totals

snapshot_date is mapped to the beginning of its calendar quarter. For 2026-06-19, bond_time is 2026-04-01. join_bonds performs a validated many-to-one left join on area_code and bond_time. All listings are retained. bond_row_matched distinguishes the absence of a record from a matched record whose rent is missing. No unmatched metric is filled with zero.

### Calculate and summarise

Median long-term nightly rent equals Median Rent divided by seven. Each listing gap equals its nightly price minus that estimate. summarise_locations groups by bond_time, area_code and area_name, retaining the quarter in the output. It reports all listings, priced listings and usable price gaps separately. rank_gaps applies the configured minimum to observed gaps, then ranks eligible locations within each quarter.

### Validate and export

sanity_check verifies preserved row counts and listing keys, summary counts, quarter alignment, nightly units, gap arithmetic and missing unmatched values. write_outputs saves CSVs and SQLite, checks the SQLite joined row count, creates plots and the report, and writes the completion marker last. The current run passes 10 analytical checks. The separate delivery verification compares all six SQLite tables with CSV contents and checks regression against Deliverable 5.

## 4 Coding and software strategies

### Clear responsibilities and explicit data flow

run_pipeline.py orchestrates named stages. pipeline/transforms.py contains dataframe transformations, geography.py handles cache and network access, validation.py checks invariants, and outputs.py writes artifacts. Functions accept explicit inputs and return outputs. Transformations copy their inputs rather than mutating global data. Docstrings and descriptive names explain purpose and assumptions without commenting on every obvious line.

This follows the supplied Data Wrangling Pipeline and Modularity lecture: page 30 describes meaningful modules, pages 34 to 36 illustrate descriptive functions and explicit inputs and outputs, page 37 recommends project-relative paths, and page 38 recommends scripted changes instead of manual data-file edits.

### Configuration and reproducible automation

config.json separates tunable settings from transformation logic. Named constants define the weekly conversion and SA2 source fields. Defaults are relative to the script location, and path overrides support other machines. requirements.txt records the tested package versions; the run manifest records the actual environment. A Makefile runs analysis, the persisted sanity check, verification and Word and Markdown document generation in dependency order. The supplied example-automated-pipeline.zip demonstrates the same overall strategies through separate R stages, config.yaml, inspectable intermediates and a Makefile.

The Makefile intentionally executes a complete verification run rather than implementing per-stage timestamp caching. A normal rerun replaces only generated Deliverable 6 outputs. Offline execution reuses the fixed supplied cache; network mode can change geographic results and needs its own review. For a failed live run, supply its checkpoint as --cache and choose a new --output folder.

### Fail early and verify meaningful invariants

Invalid schemas, malformed dates or numbers, duplicate keys and ambiguous quarterly snapshots stop the run with an actionable error. 19 automated edge tests exercise double counting, join expansion, missing prices, duplicate keys, quarter separation, offline cache reuse, failed-cache retries, timeout handling and arithmetic corruption. Tests use mocked network responses; the current validation does not claim a fresh live API check.

### Preserve evidence and review assumptions

Earlier deliverables and raw data remain unchanged. inputs/source_materials_manifest.json records reviewed-source fingerprints. The revised join uses validated pandas merges; SQLite persists the resulting tables for inspection. This makes the many-to-one constraint explicit and produces the same existing listing values and all 174 previous location statistics. The observed-gap ranking threshold is an intentional method correction described in the change notes.

Remaining review limits are geographic correctness and boundary compatibility: cached assignments are structurally checked but not independently recomputed against polygons, and the available files do not establish a shared SA2 vintage for the bond and Airbnb geography. Matching codes alone cannot resolve this; unmatched records and coverage are retained for review.
