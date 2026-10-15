# Christchurch Airbnb and tenancy rental comparison

This project builds a reproducible comparison of Airbnb asking prices and private tenancy bond rents across Christchurch City, including Banks Peninsula. It covers the eleven monthly Airbnb snapshots from October 2025 to August 2026 and joins each listing to the matching SA2 2019 area and calendar quarter.

All code, inputs, caches and outputs are contained in this folder. The supplied files in `Raw data/` and the original June listing file are preserved. Airbnb source downloads are stored separately in `data/raw/`; downloaded monthly tenancy releases and their manifest are in `Raw data/`.

## Open the results

- [Analysis workbook](outputs/excel/christchurch_rental_analysis.xlsx): overview, a dedicated July/August citywide comparison, monthly trends, area comparisons, sensitivity groups, coverage, cleaning audit and a **Price recovery check** sheet.
- [Merged datasets workbook](outputs/excel/christchurch_merged_datasets.xlsx): listing-level panel, quarterly area bond benchmarks, official monthly city bonds, detailed bond categories, field dictionary and source inventory.
- [Interactive price map](outputs/maps/christchurch_price_bars.html): open this HTML file in a browser. Select a month, comparison group and display. Click an area or bar for prices and sample sizes. The default month is August 2026. The city summary uses official monthly rents; area bond bars and area gaps remain unavailable for July/August. Select June for the latest usable suburb comparisons.
- [Figures](outputs/figures/): nine figures, each provided as PNG and PDF.
- [GIS layers](outputs/gis/christchurch_rental_comparison.gpkg): open in QGIS or another GeoPackage-compatible GIS. Includes listing-month points, latest comparable areas and latest snapshot areas.
- [CSV tables](outputs/tables/) and [SQLite database](outputs/christchurch_rentals.sqlite): machine-readable results.
- [Quality results](outputs/data_quality.json) and [run manifest](outputs/run_manifest.json): checks, input hashes, code hashes, output hashes and coverage limitations.

## Data availability that affects interpretation

All eleven monthly listing snapshots are available. The source summary CSVs contain no prices for December 2025, January 2026 or February 2026. A follow-up investigation downloaded all eleven matching detailed NZ files and the three missing-month calendar files. Exact Christchurch ID and scrape matching found **zero recoverable additional prices**. Every one of the 3,440,867 Christchurch calendar rows scanned for those three snapshots also has empty `price` and `adjusted_price` fields. These records support listing counts but not price comparisons. The analysis cannot be price-complete from the available source files; blanks are retained rather than estimated. Other NZ cities are excluded before comparison.

The detailed suburb bond source currently ends at the April–June 2026 quarter. July and August Airbnb prices remain available, but same-quarter suburb bond comparisons are unavailable. Official monthly Christchurch City (TA 060) data provide citywide medians for the whole period, including NZ$550/week in July and August. Citywide comparisons are separate from SA2 comparisons; no citywide rent is assigned to a suburb or listing. No rents or prices are carried forward or imputed.

The executed build retains 35,796 listing-month records representing 4,264 distinct listing IDs. The official city geography contains 172 SA2 2019 areas. These figures describe this source revision; see the generated quality file for the result of a later rebuild.

The source comparison CSVs and Christchurch-only detailed/calendar extracts are in `Raw data/inside_airbnb_christchurch_checks/`. The full NZ archives are preserved separately as publisher inputs under `data/raw/airbnb/detailed/` and `calendar/`; they do not expand the Christchurch analysis population. The **Price recovery check** sheet in both workbooks records the outcome for each month.

## Run in VS Code

The workspace selects `.venv/bin/python`. In the VS Code terminal, run:

```bash
.venv/bin/python run_pipeline.py
```

This rebuilds the analysis from the local inputs and geographic cache without API requests. To retrieve missing public source files, refresh the quarterly bond release and verify a sample against the Koordinates point API:

```bash
.venv/bin/python run_pipeline.py --download
```

For another computer, use Python 3.12:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Enter the Koordinates key in `.env` and run with `--download`. Keep `.env` local. The map uses locally stored Leaflet assets, polygons, place labels and a distance scale. It makes no external basemap tile requests, avoiding the blocked OpenStreetMap tile response. The map can be opened directly from disk. An optional local server is:

```bash
.venv/bin/python -m http.server 8765 --bind 127.0.0.1 --directory outputs
```

Then open `http://127.0.0.1:8765/maps/christchurch_price_bars.html` in a browser.

Run the regression tests with:

```bash
.venv/bin/python -m pytest -q tests
```

Re-run the source investigation from its local archives:

```bash
.venv/bin/python tools/check_airbnb_price_gaps.py
```

Add `--download` only when an archive is missing, then rebuild with `run_pipeline.py`. This audits exact source values; it does not generate replacement prices from nearby months, calendar averages or modelled revenues.

## Comparison method

The main group is entire homes/apartments with minimum stays of 1–30 nights. The same outputs also show all room types, entire short stays with advertised availability, and entire short stays more than 150 metres from an SA2 boundary.

Airbnb prices are nightly asking prices in NZD. Tenancy prices are published weekly medians, converted to nightly equivalents by dividing by seven. The join is many-to-one on SA2 code and quarter, with no loss or duplication of Airbnb rows. It uses the published `ALL` dwelling and `ALL` bedroom category rather than adding overlapping categories together.

City summaries also join the official monthly TA 060 source by exact calendar month. `citywide_difference_of_medians_nzd` equals the city Airbnb median minus the city monthly bond weekly median /7. It differs from `median_listing_gap_nzd`, which uses matched SA2-quarter rents. For the primary entire-home group, July and August city differences are NZ$170.43 and NZ$167.43 per night. The official source rows are in the **City monthly bonds** sheet of both workbooks.

The geographic reference is SA2 **2019**, because Tenancy Services documents that vintage for its bond data. The assignment's linked SA2 2026 geography has changed boundaries and is not used as if it were interchangeable. Koordinates provides the 2019 polygons through layer 98779, filtered to Christchurch territorial authority 060. A live test and 25 point queries against SA2 layer 98970 verify the assignment method. Coordinates use EPSG:4326, and boundary distances use NZTM EPSG:2193.

The price gap is descriptive. It does not measure rental profit, match properties on bedrooms or quality, account for Airbnb fees and occupancy, or establish that Airbnb changes long-term rents. Airbnb coordinates are anonymised, so areas near boundaries are uncertain. Published bond counts are privacy rounded and low-count selections may be suppressed.

Airbnb snapshot counts and active bonds describe different markets. Neither is a count of currently advertised vacancies. Do not sum monthly listing counts or quarterly active-bond stocks as distinct properties across time.

## Project files

```text
run_pipeline.py           One-command orchestration
requirements.txt          Exact installed Python dependency versions
config/project.json       Scope, geography and comparison settings
pipeline/
  sources.py              Versioned source downloads and provenance
  geography.py            Koordinates API, cached polygons and spatial validation
  transforms.py           Cleaning, exact joins and monthly summaries
  city_monthly.py         Official city monthly benchmarks; separate from SA2 rents
  validation.py           Data and persisted-workbook checks
  figures.py              Reproducible scientific charts and maps
  maps.py                 Interactive map builder
  map_template.html       Map interface and controls
  workbooks.py            Excel exports and field definitions
tests/                    Regression tests for material analytical risks
docs/                     Methodology and design principles
tools/                    Source download and verification helpers
data/raw/                 Local source files and source manifest
data/cache/               Local GIS cache and API validation results
outputs/                  Excel, figures, map, GIS, CSV, SQLite and audit files
.vscode/                  Interpreter and debugging settings
```

## Sources and attribution

- [Inside Airbnb data](https://insideairbnb.com/get-the-data/) and [data assumptions](https://insideairbnb.com/data-assumptions/). Downloaded summary `listings.csv` files, with dates and hashes recorded in the source manifest.
- [MBIE Tenancy Services rental bond data](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/), credited to the Ministry of Business, Innovation and Employment. The source page describes rounding, suppression, geographic definitions and provisional data during system migration.
- [Stats NZ SA2 Higher Geographies 2019](https://datafinder.stats.govt.nz/layer/98779/) and [SA2 2019](https://datafinder.stats.govt.nz/layer/98970/), accessed through Koordinates. Public layer metadata, including licence information, is retained in the geographic cache.
- [Koordinates vector query documentation](https://help.koordinates.com/query-api-and-web-services/vector-query/).
- [Leaflet](https://leafletjs.com/) for interactive mapping. The reference map uses the cached Stats NZ geography; no OpenStreetMap tiles are requested.

## AI assistance and publication

Code and technical documentation were developed with OpenAI ChatGPT through Codex. See [design principles](docs/design_principles.md) for the implemented software strategy and [methodology](docs/methodology.md) for analytical decisions.

The folder is inside an existing parent Git repository. No nested repository, remote, commit or publication was created. The local `.gitignore` excludes raw data, outputs, caches, the virtual environment and API credentials. Review the intended repository and selected files before publishing.
