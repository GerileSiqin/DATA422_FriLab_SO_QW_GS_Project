# Task: Brave price comparison
# Goal: Compare Airbnb price distributions for all New Zealand and Christchurch City in the same plot.
# Orange workflow:
# CSV File Import -> Select Rows -> Python Script -> Distributions
# In Select Rows, keep listings where price is defined and price <= 1000.
# This script creates a new variable called comparison_group with two groups:
# 1. All New Zealand
# 2. Christchurch City
# In Distributions, use price as the variable and comparison_group as Split by.


import numpy as np
from Orange.data import Domain, DiscreteVariable, Table

data = in_data

# Get neighbourhood_group column
ng_var = data.domain["neighbourhood_group"]
ng_col = data.get_column(ng_var)

# Convert neighbourhood_group values to readable text
ng_labels = np.array([ng_var.repr_val(x) for x in ng_col])

# Select Christchurch City rows
chch_mask = ng_labels == "Christchurch City"
chch_data = data[chch_mask]

# Create new categorical variable for comparison
group_var = DiscreteVariable(
    "comparison_group",
    values=["All New Zealand", "Christchurch City"]
)

# Combine all New Zealand rows and Christchurch City rows
new_X = np.vstack((data.X, chch_data.X))

# Add group labels
# 0 = All New Zealand
# 1 = Christchurch City
group_codes = np.concatenate((
    np.zeros(len(data)),
    np.ones(len(chch_data))
))

new_X = np.column_stack((new_X, group_codes))

# Combine Y values
if data.Y.ndim == 1:
    new_Y = np.concatenate((data.Y, chch_data.Y))
else:
    new_Y = np.vstack((data.Y, chch_data.Y))

# Combine meta values
new_metas = np.vstack((data.metas, chch_data.metas))

# Create new domain with comparison_group added
new_domain = Domain(
    data.domain.attributes + (group_var,),
    data.domain.class_vars,
    data.domain.metas
)

# Output new data
out_data = Table.from_numpy(
    new_domain,
    new_X,
    new_Y,
    new_metas
)