# Project Progress

## 3 August 2026 — Added Christchurch Airbnb workflow

- Added `Airbnb-Christchurch-NZ.ows` to the project repository.
- The file contains an Orange Data Mining workflow for exploring and analysing the Christchurch Airbnb dataset.
- R remains the primary programming language for the overall project.
- This Orange workflow uses Python as its embedded language and serves as a supplementary data-exploration resource.
- The file is for testing the Orange app, so please feel free to add comments or make any changes.
- Contributor: Qi Wang

## 6 August 2026 — Completed Orange Airbnb data-wrangling tasks

- Expanded `Airbnb-Christchurch-NZ.ows` into a complete Orange workflow using the New Zealand Airbnb listings dataset.
- Created price-distribution histograms for all New Zealand listings and Christchurch City listings, including filtered views that reduce the effect of extreme prices.
- Added a Python Script step that dynamically calculates `days_since_last_review` from each listing's last-review date to the current date.
- Compared the distribution of `days_since_last_review` for all listings with the distribution for listings priced below 1,000.
- Identified the most-reviewed 10% of New Zealand listings using equal-frequency discretisation and found 343 of these listings in Christchurch City.
- Exported eight HTML reports covering the results of Tasks 1, 2, and 3.
- Committed and pushed the updated Orange workflow and reports to the `orange-airbnb-workflow` branch on GitHub.
- Contributor: Qi Wang
