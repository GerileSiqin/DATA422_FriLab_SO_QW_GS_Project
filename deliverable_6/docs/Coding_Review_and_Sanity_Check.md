# Pipeline coding review and tutor change notes

DATA422 Deliverable 6  |  30 September 2026

The review revisits the Airbnb preparation and Qi cleaning scripts in Deliverables 3 and 4 and the comparison pipeline in Deliverable 5. Deliverable 6 implements a revised comparison pipeline; it reads the same date-bearing Airbnb input and cleaned bond input and preserves earlier deliverables. These notes record changes at the level of purpose and behaviour, rather than individual lines.

OpenAI ChatGPT through Codex was the AI used to assist with the code review, refactoring, tests and document drafting. The documents were reconciled with the implemented code and the executed verification results.

## High level changes and reasons

### Separate the orchestration from focused stages

The large Deliverable 5 main function was split into configuration, pure dataframe transformations, geography, validation and output modules. Each stage has descriptive names and explicit inputs and outputs. This makes the join and calculation logic easier to read, reuse and test separately from files and network calls. The earlier Deliverable 4 scripts contain useful inspection and report logic but also run prompts and data loading at import time; they are retained as historical scripts rather than imported into the revised workflow.

### Move settings into configuration and add automation

Worker count and the observed-gap minimum are stored in config.json with command-line overrides. Input and output paths use project-relative defaults. A Makefile runs the analytical workflow, sanity demonstration, delivery verification and document generation. This adapts the supplied automated R pipeline example to the existing Python project without changing languages or introducing a new workflow platform.

### Strengthen validation before calculations

The revised pipeline rejects missing fields, malformed dates and numeric values, invalid IDs and coordinates, duplicate listing-snapshot keys and duplicate bond location-quarter totals. The previous pipeline sometimes converted malformed data silently to missing. Failure is now explicit. Legitimate missing prices are retained, so validation does not discard listings simply because a price is absent.

### Use the input that retains the required date

Deliverable 4 christchurch_listings_clean_qi.csv removes snapshot_date and retains month_year. Deliverable 5 needs the snapshot date to derive a quarter. The revised pipeline therefore keeps Deliverable 3 christchurch_airbnb_cleaned.csv as its default Airbnb input, rather than claiming that the narrower Qi listing file feeds the join. The design document explicitly states this boundary and does not invent snapshot dates.

## Method corrections and output changes

### Keep quarters separate and constrain the join

The previous location summary grouped only by SA2 and could mix prices and maximum bond metrics across quarters. The revised summary includes bond_time. It permits at most one snapshot per quarter; additional monthly snapshots require an explicit selection step. A validated many-to-one left join on SA2 and quarter now enforces the intended grain. Published ALL/ALL bond totals are retained rather than summing overlapping breakdowns.

### Apply the gap minimum to observed prices

The previous ranking required five total Airbnb listings, even if fewer had prices. The revised ranking requires at least 5 usable listing gaps, while retaining the all-listing count separately. This makes the minimum refer to the observations actually used to calculate the median. The documented choice is configurable; it is a stricter denominator and changes the eligible locations.

In this run, Bryndwr South, Queenspark, Avonside, Sydenham West have at least five listings but only four usable price gaps each, so they leave the ranking. Eligible locations decrease from 95 to 91. Bryndwr South was the previous leading result, NZ$287.64 from four observed prices among five listings. Under the revised rule, Wigram North, Holmwood share the highest rounded gap, NZ$242.71.

### Distinguish missing data and count denominators

The outputs now distinguish all listings, priced listings and usable listing gaps, and record whether a bond row matched. Unmatched rents remain missing; plots label missing bond counts. The earlier Christchurch Central report said 117 listings because it counted only nonmissing prices. The revised report states 119 listings and 117 priced observations, retaining its NZ$250.00 median.

### Make cache reuse and error handling reliable

A complete cache can now reproduce results without an API key or network call. Failed cache rows are treated as pending in live mode instead of permanently completed. Timeout handling no longer assumes every exception has a reason attribute. Cache checkpoints are written atomically and input caches remain unchanged. Query errors retain concise status codes and do not save request URLs, API keys or server response bodies.

### Record provenance and keep documents consistent

Generated outputs include an input and code hash manifest, actual software versions, measured quality checks and a completion marker. The document builder reads the verified result files for counts and results. The revised pandas join replaces the embedded SQL transformation; SQLite continues to store all six output tables. Independent verification confirms that all prior joined values and all 174 location statistics are preserved. Changes to ranking membership are deliberate and recorded above.

## Sanity check example for the tutor

A left join can appear successful while duplicating listings or attaching the wrong period. A useful sanity check combines row and key preservation with an independent unit calculation. Run sanity_check_example.py after the pipeline; it reloads the saved CSVs and checks the persisted output rather than relying on an in-memory preview.

### Expected conditions

- The left join must preserve the input row count and the set of listing ID and snapshot date keys, with no duplicate listing-snapshot keys.

- A June 2026 snapshot must map to the quarter beginning 2026-04-01. Every location summary count must reconcile with the listing-level output.

- Nightly bond rent must equal weekly rent divided by seven. The price gap must equal the Airbnb nightly price minus that estimate. Missing unmatched bond values must remain missing.

```python
if len(joined) != len(airbnb):
    raise ValueError("Left join changed the row count")
expected_gap = price - weekly_rent / 7.0
# Compare the saved gap with a small floating-point tolerance.
```

### Actual hand calculation

Listing 319770 has snapshot date 2026-06-19, mapped to bond quarter 2026-04-01. Its Airbnb price is NZ$201.00 per night, and the matched median weekly rent is NZ$530.00. The expected nightly bond rent is 530 / 7 = NZ$75.714286. The expected gap is 201 - 530 / 7 = NZ$125.285714, matching the saved value within numerical tolerance.

### Executed evidence

The executed June 2026 run retains 3,469 listings across 174 SA2 groups. All 3,469 listings have cached SA2 assignments. 2,673 listings match a bond total (77.1%); 2,474 have a usable price gap. The 274 missing Airbnb prices are retained.

All 10 analytical checks and 19 edge tests passed. The persisted-output demonstration passes nine dataframe checks. Delivery verification confirms matching CSV and SQLite contents for all six tables, unchanged input fingerprints, the corrected ranking denominator and agreement with Deliverable 5 on existing joined values and location statistics. Deliberately corrupted gaps and expanded joins fail the tests, showing that the checks detect these errors.

### Materials to show the tutor

Show this change log, the separate design-principles document, run_pipeline.py and its named modules, sanity_check_example.py, and results/test_results.txt plus the JSON verification reports. The design document maps the actual inputs, outputs, stages and adopted coding strategies to the revised implementation.

Course references are the supplied example-automated-pipeline.zip and Data Wrangling W03 DATA201 422 pipeline modularity, particularly pages 30 and 34 to 38. The analytical checks do not independently validate the geographic cache against polygons or resolve the SA2 vintage of the bond data. Those limits remain explicit in the design document.
