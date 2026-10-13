"""
Create Deliverable 7 visualisations.

This script:
1. Creates an updated Airbnb median-price plot for:
   - Christchurch overall
   - Christchurch Central
2. Creates the Airbnb-Bond median rental-gap plot.
3. Saves both plots in the output folder.

Author: Gerile
"""

import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------------
# File paths
# -----------------------------------

AIRBNB_PRICE_FILE = (
    "output/4_airbnb_price_by_time.csv"
)

RENTAL_GAP_FILE = (
    "output/4_rental_gap_by_time.csv"
)


AIRBNB_PRICE_PLOT = (
    "output/5_airbnb_price_over_time.png"
)

RENTAL_GAP_PLOT = (
    "output/5_rental_gap_over_time.png"
)


# ===================================
# Plot 1:
# Airbnb median price over time
# ===================================

print("\n===================================")
print("Creating Airbnb price plot")
print("===================================")


# -----------------------------------
# Read Airbnb price analysis
# -----------------------------------

price_df = pd.read_csv(
    AIRBNB_PRICE_FILE
)


# -----------------------------------
# Check required columns
# -----------------------------------

required_price_columns = [
    "month_year",
    "christchurch_median_price",
    "central_median_price"
]


for column in required_price_columns:

    if column not in price_df.columns:
        raise ValueError(
            f"Missing Airbnb price column: {column}"
        )


# -----------------------------------
# Prepare date column
# -----------------------------------

price_df["month_year"] = pd.to_datetime(
    price_df["month_year"]
)

price_df = price_df.sort_values(
    "month_year"
)


print("\nAirbnb price data:")
print(price_df)


# -----------------------------------
# Create Airbnb price plot
# -----------------------------------

plt.figure(
    figsize=(9, 5)
)


plt.plot(
    price_df["month_year"],
    price_df["christchurch_median_price"],
    marker="o",
    label="Christchurch overall"
)


plt.plot(
    price_df["month_year"],
    price_df["central_median_price"],
    marker="o",
    label="Christchurch Central"
)


plt.title(
    "Median Airbnb Nightly Price in Christchurch",
    fontweight="bold"
)


plt.xlabel(
    "Month",
    fontweight="bold"
)


plt.ylabel(
    "Median Airbnb price ($ per night)",
    fontweight="bold"
)


# -----------------------------------
# Month labels
# -----------------------------------

month_labels = (
    price_df["month_year"]
    .dt.strftime("%b %Y")
)


plt.xticks(
    price_df["month_year"],
    month_labels,
    rotation=45
)


# -----------------------------------
# Plot formatting
# -----------------------------------

plt.legend()

plt.grid(
    axis="y",
    alpha=0.3
)


ax = plt.gca()

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)


plt.tight_layout()


# -----------------------------------
# Save Airbnb price plot
# -----------------------------------

plt.savefig(
    AIRBNB_PRICE_PLOT,
    dpi=300
)


print("\nSaved:")
print(AIRBNB_PRICE_PLOT)


plt.show()


# ===================================
# Plot 2:
# Rental gap over time
# ===================================

print("\n===================================")
print("Creating rental-gap plot")
print("===================================")


# -----------------------------------
# Read rental-gap analysis
# -----------------------------------

gap_df = pd.read_csv(
    RENTAL_GAP_FILE
)


# -----------------------------------
# Check required columns
# -----------------------------------

required_gap_columns = [
    "month_year",
    "median_rental_gap"
]


for column in required_gap_columns:

    if column not in gap_df.columns:
        raise ValueError(
            f"Missing rental-gap column: {column}"
        )


# -----------------------------------
# Prepare date column
# -----------------------------------

gap_df["month_year"] = pd.to_datetime(
    gap_df["month_year"]
)

gap_df = gap_df.sort_values(
    "month_year"
)


print("\nRental-gap data:")
print(gap_df)


# -----------------------------------
# Create rental-gap plot
# -----------------------------------

plt.figure(
    figsize=(9, 5)
)


plt.plot(
    gap_df["month_year"],
    gap_df["median_rental_gap"],
    marker="o"
)


plt.title(
    "Airbnb and Long-Term Rental Price Gap "
    "in Christchurch",
    fontweight="bold"
)


plt.xlabel(
    "Month",
    fontweight="bold"
)


plt.ylabel(
    "Median rental gap ($ per day)",
    fontweight="bold"
)


# -----------------------------------
# Month labels
# -----------------------------------

gap_month_labels = (
    gap_df["month_year"]
    .dt.strftime("%b %Y")
)


plt.xticks(
    gap_df["month_year"],
    gap_month_labels,
    rotation=45
)


# -----------------------------------
# Plot formatting
# -----------------------------------

plt.grid(
    axis="y",
    alpha=0.3
)


ax = plt.gca()

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)


plt.tight_layout()


# -----------------------------------
# Save rental-gap plot
# -----------------------------------

plt.savefig(
    RENTAL_GAP_PLOT,
    dpi=300
)


print("\nSaved:")
print(RENTAL_GAP_PLOT)


plt.show()


# ===================================
# Complete
# ===================================

print("\n===================================")
print("Plots created successfully")
print("===================================")