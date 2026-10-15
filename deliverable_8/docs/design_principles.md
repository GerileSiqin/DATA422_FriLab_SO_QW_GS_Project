# Christchurch pipeline design principles

This pipeline is implemented in Python. Code and technical documentation were developed with OpenAI ChatGPT through Codex. The design below describes the implemented code and its current limitations.

## Inputs

Versioned monthly Inside Airbnb New Zealand summary CSVs, the detailed quarterly Tenancy Services CSV, project settings in `config/project.json`, and official SA2 2019 polygons retrieved from Koordinates. Credentials are read from the local environment or `.env`. They are never included in browser map requests or output workbooks.

## Outputs

Two Excel workbooks, analytical CSV tables, a SQLite database, nine PNG/PDF figures, an interactive HTML map with locally cached mapping assets, and a GeoPackage. Quality JSON and a run manifest record coverage limitations, source hashes, code hashes and output hashes. Completion is recorded after the export checks finish.

## Main steps

1. Discover monthly publisher snapshots and download immutable source files. Preserve revised quarterly bond files under content-hash filenames.
2. Obtain city SA2 2019 polygons through Koordinates, cache the result, and test a known coordinate before any validation batch.
3. Filter and clean records while retaining identifiers, missing values, source-row lineage and quality flags.
4. Assign areas locally from API-supplied polygons, calculate boundary uncertainty flags, and compare a deterministic sample with the point API.
5. Select unique bond benchmarks and join on area and quarter with explicit many-to-one validation.
6. Summarise the primary and sensitivity groups, produce outputs, and verify persisted data.

## Software strategy

Each module owns one task: source access, geography, transformations, validation, figures, interactive mapping or workbook export. The command-line entry point orchestrates those modules rather than duplicating transformations in separate scripts. Project-relative paths allow relocation; source manifests identify exact input versions.

Use descriptive column names and document definitions. Pass configuration and data explicitly. Reject invalid schemas and conflicting keys rather than silently dropping conflicts. Preserve missing measurements rather than presenting them as zero. Reuse cached polygons instead of submitting thousands of repeated point queries. Public metadata uses anonymous requests, while protected query endpoints use header authentication and bounded retry/backoff. API errors do not expose credentials.

Save source manifests and geographic cache metadata atomically. Analytical outputs are rebuilt at stable paths; a failed or interrupted build may leave partial output files, so check `outputs/run_status.json` and use results only after a successful complete run. Source files remain separate from generated outputs.

The pinned Python requirements and local virtual environment support reproducibility. Regression tests exercise large identifier preservation, duplicates, missing prices, minimum stays, date mapping, exact-quarter joins, overlapping bond categories, missing snapshots and zero-listing areas. Runtime checks independently verify input hashes, uniqueness, row counts and price arithmetic. Workbook checks read saved exports and preserve identifiers as text.

## Sanity check example

A listing priced at NZ$200 per night in June 2026 maps to the April–June quarter. A matching SA2 bond median of NZ$700 per week gives a nightly equivalent of NZ$100 and a price gap of NZ$100. A July record must not reuse that April quarter: without a July-quarter bond row, its gap remains missing. The regression tests execute both cases.

## Limits

API agreement does not recover the true address behind an anonymised coordinate. The summary Airbnb input does not support bedroom matching. The current source revision has three months without prices and no July–September suburb bond quarter. The interactive map uses only local assets, Stats NZ polygons and place labels; it does not request remote basemap tiles. Its city monthly summary is separate from the suburb layers, which retain missing quarter rents. The pipeline does not create or publish a remote repository.
