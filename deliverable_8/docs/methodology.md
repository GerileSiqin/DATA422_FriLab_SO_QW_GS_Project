# Christchurch rental comparison methodology

## Population and time

Use Inside Airbnb's published New Zealand monthly summary snapshots, select `neighbourhood_group = Christchurch City`, and retain one observation per listing ID and snapshot month. The requested period is October 2025 through August 2026. Publisher dates and scrape identifiers come from its snapshot catalogue; the older October 5 snapshot is verified against the public archive URL.

Use the latest retrieved revision of the detailed quarterly tenancy CSV. Restrict its dates to the quarters intersecting the requested period and its location codes to the official Christchurch SA2 2019 set. Missing quarters remain unavailable. Never derive snapshot dates from review dates or relabel a file based on its filename alone.

## Cleaning and lineage

Preserve the raw downloads and supplied files. Read identifiers as strings, since many Airbnb IDs exceed Excel's reliable numeric precision. Keep source-file paths and original CSV row numbers in prepared data. Remove exact duplicate records; stop on conflicting repeated listing IDs within a snapshot or conflicting bond category keys.

Parse coordinates and numeric fields explicitly. Retain missing prices and zero-availability listings for counts. Nonpositive prices become missing and are audited. Out-of-range availability and invalid minimum stays are flagged and set missing. Prices above the monthly room-type 99th percentile are flagged and retained. Review dates after the publisher's snapshot date remain flagged rather than causing listing deletion.

## Geographic alignment

Tenancy Services states that its location IDs use SA2 2019. Use the official 2019 higher-geography layer 98779 with `TA2019_V1_00 = 060` to obtain Christchurch City polygons, including Banks Peninsula. Match coordinates with strict point-in-polygon containment. Do not select a nearby area merely because no polygon contains the point.

Validate the API configuration with Christchurch Central point `(172.6362, -43.5321)`, which must return SA2 326600. Verify 20 deterministically sampled areas and five boundary-adjacent cases against Koordinates SA2 2019 layer 98970. These checks test consistency with the API, not the accuracy of anonymised Airbnb coordinates.

Both coordinates and API geometries use WGS84 EPSG:4326. Calculate boundary distances in metres with NZTM EPSG:2193. Inside Airbnb says listing coordinates may be displaced by about 150 metres, so flag points within 150 metres of their assigned boundary. Supply a sensitivity group that excludes these listings. A 2019 polygon match is an assignment to an approximate published coordinate, not a verified property address.

## Rent and temporal alignment

Map a snapshot to its calendar quarter start: June 2026 maps to April 1, and July–August map to July 1. Select the bond `ALL` dwelling type and `ALL` number-of-beds row. Enforce uniqueness by SA2 and quarter before a left join from Airbnb. A missing bond row differs from a matched row with suppressed rent.

Calculate nightly bond equivalent as weekly median rent divided by seven. Calculate each listing's observed gap and price ratio only where both source prices are available. These compare two accommodation products. Summary Airbnb data do not include bedroom counts, so bedroom matching is not supported. No net returns, occupancy estimates or causal effects are inferred.

## Summaries and comparisons

The primary group is entire homes/apartments with minimum stays of 1–30 nights. Sensitivity groups include all room types, entire short stays with availability above zero, and entire short stays beyond the boundary-warning distance.

Retain every official city SA2 in an area-month-segment grid, including areas with no observed listings. A missing snapshot produces missing counts, while a present snapshot with no listings in an area produces a zero. Report price and usable-gap denominators separately. Rank gaps only where at least five matched positive Airbnb prices are observed. This threshold is not a significance test or confidence measure.

Medians are calculated from listing observations, not by averaging area medians. The city chart uses the official monthly Christchurch City (TA 060) median weekly bond rent /7. Its citywide gap is the difference of citywide medians. The older listing-weighted median of matched area bond benchmarks remains a separate field, as does the median of listing-level gaps; neither is substituted for the official city median. Airbnb price quartiles describe observed spread; they are not confidence intervals.

Compare snapshot Airbnb listing counts with published active bonds as indicators of market scale. Label both explicitly. Bond lodgements are a quarterly flow and active bonds are a stock measure; neither is a direct vacancy count. Do not sum these repeated stocks across months.

## Known source gaps

The retrieved December 2025, January 2026 and February 2026 summary CSVs have zero observed price values across New Zealand. Listing-count and geographic analyses remain possible for these months. Price trends contain gaps.

The retrieved suburb bond file contains quarters through April–June 2026. July and August Airbnb records therefore have no same-quarter suburb bond comparison. The pipeline never fills them using the previous quarter.

Tenancy Services applies fixed random rounding to base three and suppresses low-count selections. It also describes recent releases as provisional during bond-system migration. Counts and rent comparisons should retain these source limitations.

## Sources

[Inside Airbnb downloads](https://insideairbnb.com/get-the-data/), [Inside Airbnb assumptions](https://insideairbnb.com/data-assumptions/), [MBIE rental bond data](https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/), [Stats NZ layer 98779](https://datafinder.stats.govt.nz/layer/98779/), [Stats NZ layer 98970](https://datafinder.stats.govt.nz/layer/98970/), and [Koordinates query API](https://help.koordinates.com/query-api-and-web-services/vector-query/).

## Official city monthly extension

The monthly territorial-authority CSV is preserved in `Raw data/`, with its download URL and SHA-256 in `tenancy_download_manifest.json`. Select code 060 (normalising the source value 60), verify the city name, enforce one row per month, and join to city summary rows by exact snapshot month. No carry-forward is used. City monthly rents are not copied into the listing or area tables. July and August 2026 both publish NZ$550/week (NZ$78.57142857/night equivalent). The primary Airbnb medians are NZ$249 and NZ$246/night, giving differences of citywide medians of NZ$170.43 and NZ$167.43/night. These are different markets and property sets.

The city source has observations throughout the scope. December–February comparisons remain missing because the Airbnb price fields are empty. July/August suburb-quarter gaps remain missing even though citywide comparisons are available. Nine figures include a dedicated July/August citywide chart; suburb ranking and static maps retain June, their latest usable month. The interactive map starts in August, shows city values in a separate panel, and uses local Stats NZ boundaries and labels without remote tile requests.

## Missing-price source investigation, 15 October 2026

All eleven monthly detailed NZ `listings.csv.gz` archives were matched to the summary Christchurch City listing IDs and, where available, the exact publisher scrape ID. Detailed region labels independently agree with Christchurch City. No other city or snapshot supplies a replacement value. All 35,796 Christchurch listing-months have matching detailed records, but no missing summary price has a positive detailed price. Whole-NZD summary rounding differs from detailed cents for some observed records; these precision differences are audited, while the established summary price series is retained.

For the wholly missing-price snapshots, complete calendar scans filtered by the same Christchurch IDs inspected 1,160,703 December, 1,115,809 January and 1,164,355 February listing-date records. None has a positive `price` or `adjusted_price`. Calendars describe future stay dates and are not substituted for snapshot asking prices. No statistical imputation, neighbouring-month interpolation, city substitution or reverse calculation from modelled revenue is used. A price-complete series cannot be produced from these published files.

`tools/check_airbnb_price_gaps.py` reproduces the investigation, with archive hashes and results in `Raw data/inside_airbnb_christchurch_checks/investigation_manifest.json`. Both workbooks include Price recovery check. Figures shade the months with empty source prices, and the map footer records the checked scope and outcome. The tenancy gaps have separate causes and are unaffected by Airbnb downloads.
