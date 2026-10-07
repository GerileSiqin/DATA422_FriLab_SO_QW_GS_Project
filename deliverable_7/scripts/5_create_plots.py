import pandas as pd
import matplotlib.pyplot as plt


# File paths
INPUT_FILE = "output/4_rental_gap_by_time.csv"
OUTPUT_FILE = "output/5_rental_gap_over_time.png"


# -----------------------------------
# 1. Read analysis results
# -----------------------------------

df = pd.read_csv(
    INPUT_FILE
)


print("\n-----------------------------------")
print("Creating rental-gap plot")
print("-----------------------------------")


# -----------------------------------
# 2. Check required columns
# -----------------------------------

required_columns = [
    "month_year",
    "median_rental_gap"
]

for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            "Missing required column: " + column
        )


# -----------------------------------
# 3. Prepare month column
# -----------------------------------

df["month_year"] = pd.to_datetime(
    df["month_year"]
)


# -----------------------------------
# 4. Sort by month
# -----------------------------------

df = df.sort_values(
    "month_year"
)


# -----------------------------------
# 5. Create line plot
# -----------------------------------

plt.figure(
    figsize=(9, 5)
)

plt.plot(
    df["month_year"],
    df["median_rental_gap"],
    marker="o"
)


# -----------------------------------
# 6. Add labels and title
# -----------------------------------

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
# 7. Improve month labels
# -----------------------------------

month_labels = (
    df["month_year"]
    .dt.strftime("%b %Y")
)

plt.xticks(
    df["month_year"],
    month_labels,
    rotation=45
)


# -----------------------------------
# 8. Remove top and right boundary lines
# -----------------------------------

ax = plt.gca()

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)


# -----------------------------------
# 9. Add grid and tidy layout
# -----------------------------------

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()


# -----------------------------------
# 10. Save plot
# -----------------------------------

plt.savefig(
    OUTPUT_FILE,
    dpi=300
)


# -----------------------------------
# 11. Show plot
# -----------------------------------

plt.show()


# -----------------------------------
# 12. Confirm output
# -----------------------------------

print("\nSaved:")
print(OUTPUT_FILE)