# Task: Top 10% most-reviewed listings
# Goal: Find the Airbnb listings in New Zealand with the highest number of reviews.
# Orange workflow:
# CSV File Import -> Select Rows -> Python Script -> Data Table / Distributions
# In Select Rows, keep listings where number_of_reviews is defined.
# This script ranks listings by number_of_reviews from highest to lowest,
# selects the top 10%, and counts how many of them are in Christchurch City.
# It also creates a new variable, top10_location_group, with two groups:
# 1. Christchurch City
# 2. Other New Zealand
# In Distributions, use top10_location_group to visualise the count or proportion.


import numpy as np
from math import ceil
from Orange.data import Domain, Table, DiscreteVariable

data = in_data

# Get number_of_reviews column
reviews = data.get_column("number_of_reviews")

# Remove rows where number_of_reviews is missing
valid_mask = ~np.isnan(reviews)
valid_data = data[valid_mask]
valid_reviews = reviews[valid_mask]

# Calculate top 10%
top_n = int(ceil(len(valid_data) * 0.10))

# Sort from highest number_of_reviews to lowest
order = np.argsort(valid_reviews)[::-1]

# Select top 10%
top_indices = order[:top_n]
top_data = valid_data[top_indices]
top_reviews = valid_reviews[top_indices]

# Get neighbourhood_group column
ng_var = top_data.domain["neighbourhood_group"]
ng_col = top_data.get_column(ng_var)
ng_labels = np.array([ng_var.repr_val(x) for x in ng_col])

# Create Christchurch vs Other New Zealand group
location_group = np.where(
    ng_labels == "Christchurch City",
    0,
    1
)

# Count Christchurch properties
christchurch_count = np.sum(location_group == 0)
other_count = np.sum(location_group == 1)
total_top = len(top_data)

# Print results
print("Total properties with number_of_reviews:", len(valid_data))
print("Top 10% properties:", total_top)
print("Minimum number_of_reviews in top 10%:", int(np.min(top_reviews)))
print("Christchurch City properties in top 10%:", int(christchurch_count))
print("Other New Zealand properties in top 10%:", int(other_count))
print("Percentage in Christchurch City:", round(christchurch_count / total_top * 100, 2), "%")

# Add new categorical variable
location_var = DiscreteVariable(
    "top10_location_group",
    values=["Christchurch City", "Other New Zealand"]
)

# Add the new column to the data
new_X = np.column_stack((top_data.X, location_group))

# Create new domain
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