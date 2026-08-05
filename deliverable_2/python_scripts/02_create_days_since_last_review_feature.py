# Task: Days since last review
# Goal: Create a new feature showing how many days ago each listing was last reviewed.
# Orange workflow:
# CSV File Import -> Select Rows -> Python Script -> Distributions
# In Select Rows, keep listings where last_review is defined.
# This script calculates:
# days_since_last_review = scrape/publish date - last_review date
# The scrape/publish date for this dataset is 19 June 2026.
# In Distributions, use days_since_last_review as the variable to plot its distribution.


import numpy as np
from Orange.data import Domain, Table, ContinuousVariable

# Dataset scrape/publish date: 19 June 2026
scrape_date = 1781827200

# Get last_review column
last_review = in_data.get_column("last_review")

# Calculate days since last review
days_since_last_review = (scrape_date - last_review) / 86400

# Create new numeric variable
new_var = ContinuousVariable("days_since_last_review")

# Add the new variable to the domain
new_domain = Domain(
    in_data.domain.attributes + (new_var,),
    in_data.domain.class_vars,
    in_data.domain.metas
)

# Add the new column to the data
new_X = np.column_stack((in_data.X, days_since_last_review))

# Output new data
out_data = Table.from_numpy(
    new_domain,
    new_X,
    in_data.Y,
    in_data.metas
)