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
