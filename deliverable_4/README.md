# Deliverable 4

## Choose a local input file

Run either cleaning script from the project root in a terminal:

```bash
python deliverable_4/clean_bond.py
python deliverable_4/clean_listings.py
```

Each script asks for an input path before reading data. Paste the full path to
your CSV file, or enter its folder path to use the default filename in that
folder. Press Enter to use the displayed default, or type `q` to cancel.
Invalid paths prompt you to try again. Paths containing spaces, surrounding
quotes, and `~` for your home directory are supported.

This is a terminal text prompt, not a separate graphical window. In VS Code,
use **Run Python File in Terminal** so you can type a response.

The listings input must have the same columns as the combined Christchurch
dataset from Deliverable 3 (`christchurch_airbnb_cleaned.csv`). The bond input
must use the expected rental bond CSV structure. Choosing a file changes its
location only; it does not change the cleaning rules or expected columns.
Cleaned outputs are still saved under `deliverable_4/data_processed` and
`deliverable_4/bond_data_processed`, respectively.

## Christchurch Airbnb Dataset

The Christchurch Airbnb dataset originally contained **28795 rows and 19 columns** and covered the period from **October 2025 to June 2026**.

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

| Cleaning decision | Reason | Consequence |

|---|---|---|

| Checked for exact duplicate rows and removed duplicates if found | Duplicate rows could cause listings to be counted more than once | No exact duplicate rows were found, so **0 rows were removed** |

| Kept `latitude` and `longitude` | These columns are required for Deliverable 4 and may be useful for location-based analysis | Both columns had no missing values, so **0 rows were removed** |

| Removed `license` | All 28795 values were missing, so the column contained no usable information | **1 column removed**, 0 rows removed |

| Removed `neighbourhood_group` | Every row contained the same value, `Christchurch City`, so the column did not provide additional information | **1 column removed**, 0 rows removed |

| Removed `name`, `host_id` and `host_name` | These columns are not required for the planned comparison of rental prices and property availability | **3 columns removed**, 0 rows removed |

| Removed `number_of_reviews`, `last_review`, `reviews_per_month` and `number_of_reviews_ltm` | Review-related information is not required for the planned analysis of rental prices and available properties | **4 columns removed**, 0 rows removed |

| Kept missing `price` values | There were **10667 missing price values**. All listings in December 2025, January 2026 and February 2026 had missing prices. Removing these rows would remove three complete months and affect later analysis of property availability | **10667 missing values retained**, 0 rows removed |

| Kept missing `minimum_nights` values | Only **37 values** were missing and `minimum_nights` is not essential for the planned comparison of rental prices and property availability | **37 missing values retained**, 0 rows removed |

| Kept unusually high `price` values | The highest prices were inspected by sorting the dataset by `price` and reviewing the associated listing names and IDs. Although some prices were extremely high, they were associated with identifiable listings and there was insufficient evidence to classify them as data-entry errors. | **0 rows removed** |

| Kept `id`, `neighbourhood`, `latitude`, `longitude`, `room_type`, `price`, `minimum_nights`, `calculated_host_listings_count`, `availability_365` and `month_year` | These columns are useful for identifying listings, comparing locations, analysing prices and examining property availability over time | Final dataset contains **10 columns** |

### Cleaning outcome

- Original dataset: **28795 rows and 19 columns**
- Final dataset: **28795 rows and 10 columns**
- Rows removed: **0**
- Columns removed: **9**
- Exact duplicate rows removed: **0**
- Missing `price` values retained: **10667** 
- Missing price values were retained because three complete months had no price data.
- Missing `minimum_nights` values retained: **37**

The cleaning process was designed to preserve the information needed for the next stage of the project, where the Airbnb data will be combined with rental bond data to compare **rental prices** and **property availability** over the same time period.

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

| Cleaning decision | Reason | Consequence |

|---|---|---|

| Filtered the dataset to `2025-10-01`, `2026-01-01`, and `2026-04-01` | These three quarterly periods cover the same overall period as the Christchurch Airbnb dataset, from October 2025 to June 2026 | Rows outside the target period were removed: **198868 rows** |

| Kept `TimeFrame` | This field is required for Deliverable 4 and is needed to compare the bond data over time | Column retained |

| Kept `Location Id` | This field is required for Deliverable 4 and it shows which quarter each row belongs to and is needed to compare the data across the three quarters | Column kept |

| Removed rows with missing `Location Id` | `Location Id` is needed to identify the geographic area of each row. Without it, the row cannot be confidently matched to the correct area in the Airbnb dataset | Rows with missing `Location Id` were removed: **94 rows** |

| Kept missing `Number Of Beds` values | Some dwelling types have missing `Number Of Beds` values repeatedly, suggesting that the bedroom number was not recorded for those categories rather than being accidentally missed | Missing values were kept: **876 values** |

| Kept missing `Median Rent` values | Some values may be intentionally hidden for privacy. Replacing them would require guessing, and removing the rows would also discard other useful data | Missing `Median Rent` values were kept. After filtering and removing rows with missing `Location Id`, **0 missing `Median Rent` values remained** |

| Kept all 12 columns | All columns may still be useful for later comparison of rental prices and rental market activity | No columns were removed at this stage |

| Checked for exact duplicate rows | If the same row appears more than once, the same data could be counted more than once and lead to incorrect totals or misleading results | No exact duplicate rows were found: **0 rows removed** |

### Cleaning outcome

- Original dataset: **226080 rows and 12 columns**
- Rows remaining after filtering to the three selected quarters:: **27212**
- Rows removed outside the target period: **198868**
- Rows removed because `Location Id` was missing: **94**
- Final cleaned dataset: **27118 rows and 12 columns**
- Exact duplicate rows removed: **0**
- Missing `Number Of Beds` values retained: **876**
- Missing `Median Rent` values remaining: **0**
- Columns removed: **0**

The final cleaned dataset contains only the three quarterly periods that match the Airbnb dataset and retains the information needed for later comparison of rental prices and rental market activity.

Quote from Tenancy Services (https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/)
Important:
Rental bond data migration to the new bond management system continues and therefore data remains in a provisional state at this time. Data is sourced from both legacy and new systems and may be incomplete or revised.

Reported figures may reflect system changes, data reclassification, and methodology updates rather than underlying trends. Recent data may not be directly comparable with earlier periods. There are 17,550 more active bonds because the two systems recorded the information differently. We are undertaking further data validation, clean-up, and methodology refinement to ensure consistency and accuracy of reporting going forward.

Users should exercise caution when comparing recent data releases with earlier periods, as these may not be directly comparable due to the impacts of migration and ongoing data normalisation. We will provide further information as this work continues.
