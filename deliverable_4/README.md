# Deliverable 4

## Christchurch Airbnb Dataset

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

Final cleaning decisions will be agreed on by the team after reviewing the inspection results.

### Cleaning outcome

To be completed after the team finalises the cleaning decisions.

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

To be completed after inspecting the dataset.

### Cleaning outcome

To be completed after cleaning process completed.
