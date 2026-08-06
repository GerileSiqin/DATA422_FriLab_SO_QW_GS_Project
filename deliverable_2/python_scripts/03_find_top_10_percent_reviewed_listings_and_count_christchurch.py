# Task: Find top 10% most-reviewed listings
# Orange workflow:
# CSV File Import -> Select Rows -> Python Script -> Data Table / Distributions
#
# Recommended Select Rows condition before this script:
# number_of_reviews is defined
#
# This script:
# 1. Gets the number_of_reviews column
# 2. Removes missing review values
# 3. Sorts listings from highest reviews to lowest
# 4. Selects the top 10%
# 5. Finds the cutoff number_of_reviews for the top 10%
# 6. Counts how many top 10% listings are in Christchurch City
# 7. Creates a new column called top10_location_group for visualisation

import numpy as np
from math import ceil
from Orange.data import Domain, Table, DiscreteVariable

data = in_data

# Check that data is connected to the Python Script widget
if data is None:
    raise ValueError(
        "No input data found. Please connect CSV File Import or Select Rows to the Python Script widget."
    )

# Get number_of_reviews column
reviews = data.get_column("number_of_reviews")

# Remove rows where number_of_reviews is missing
valid_mask = ~np.isnan(reviews)
valid_data = data[valid_mask]
valid_reviews = reviews[valid_mask]

# Calculate how many listings are in the top 10%
top_n = int(ceil(len(valid_data) * 0.10))

# Sort listings from highest number_of_reviews to lowest
order = np.argsort(valid_reviews)[::-1]

# Select the top 10%
top_indices = order[:top_n]
top_data = valid_data[top_indices]
top_reviews = valid_reviews[top_indices]

# Get the cutoff value for the top 10%
# This is the smallest number_of_reviews inside the top 10% group
cutoff_reviews = int(np.min(top_reviews))

# Get neighbourhood_group column
ng_var = top_data.domain["neighbourhood_group"]
ng_col = top_data.get_column(ng_var)
ng_labels = np.array([ng_var.repr_val(x) for x in ng_col])

# Create Christchurch vs Other New Zealand group
# 0 = Christchurch City
# 1 = Other New Zealand
location_group = np.where(
    ng_labels == "Christchurch City",
    0,
    1
)

# Count Christchurch properties and Other New Zealand properties
christchurch_count = np.sum(location_group == 0)
other_count = np.sum(location_group == 1)
total_top = len(top_data)

# Print results
print("Total properties with number_of_reviews:", len(valid_data))
print("Top 10% properties:", total_top)
print("Cutoff number_of_reviews for top 10%:", cutoff_reviews)
print("Christchurch City properties in top 10%:", int(christchurch_count))
print("Other New Zealand properties in top 10%:", int(other_count))
print("Percentage in Christchurch City:", round(christchurch_count / total_top * 100, 2), "%")

# Print no-code Orange test instruction
print("")
print("No-code Orange test:")
print("Use Select Rows condition:")
print("number_of_reviews is at least", cutoff_reviews)

# Add new categorical variable for Orange visualisation
location_var = DiscreteVariable(
    "top10_location_group",
    values=["Christchurch City", "Other New Zealand"]
)

# Add the new column to the top 10% data
new_X = np.column_stack((top_data.X, location_group))

# Create new Orange domain with the new column
new_domain = Domain(
    top_data.domain.attributes + (location_var,),
    top_data.domain.class_vars,
    top_data.domain.metas
)

# Output top 10% data with new location group
out_data = Table.from_numpy(
    new_domain,
    new_X,
    top_data.Y,
    top_data.metas
)
