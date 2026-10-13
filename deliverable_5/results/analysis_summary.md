# Deliverable 5 results

## Key answers

- Stats NZ dataset: **Statistical Area 2 2026**, Koordinates layer ID **123515**.
- Christchurch Central (Location ID 326600) median Airbnb nightly price: **NZ$250.00** from **117** listings.
- Largest median short-term/long-term nightly price gap (minimum five Airbnb listings): **Bryndwr South (Location ID 320800), median nightly gap NZ$287.64, based on 5 Airbnb listings**.
- SA2 enrichment coverage: **3,469/3,469 (100.0%)**.
- Bond join coverage: **2,673/3,469 (77.1%)**.

## Method

The Airbnb snapshot date is mapped to the start of its calendar quarter. The June 2026 snapshot therefore joins to the April 2026 bond quarter. A **left join from Airbnb** retains every Airbnb listing while adding the matching location-quarter bond statistics. Only bond rows with `Dwelling Type = ALL` and `Number Of Beds = ALL` are used, preventing double counting across published breakdowns.

Long-term nightly rent is the published median weekly rent divided by seven. Each listing gap is Airbnb nightly price minus that value. The location ranking uses the median listing gap and requires at least five Airbnb listings to reduce unstable small-sample extremes.

`Active Bonds` is used as the closest available proxy for long-term rental property count. The supplied Airbnb file has no beds field, so a beds comparison would not be defensible from these inputs.

## Reproducibility and privacy

The API key is read from `KOORDINATES_API_KEY` and is never written to outputs. Coordinate results are cached in `results/koordinates_coordinate_cache.csv`, so successful calls are not repeated. The SQLite database contains the two prepared tables and the SQL-joined result.
