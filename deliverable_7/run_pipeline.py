"""
Run the complete Deliverable 7 automated pipeline.

The pipeline:
1. Cleans the July and August Airbnb data.
2. Combines the new data with previous Airbnb data.
3. Adds SA2 location information and prepares time fields.
4. Runs the Airbnb price and rental-gap analyses.
5. Creates the updated plots.

Author: Gerile
"""

import subprocess
import sys


# -----------------------------------
# Start pipeline
# -----------------------------------

print("\n===================================")
print("Starting Deliverable 7 pipeline")
print("===================================")


# -----------------------------------
# Step 1: Clean new Airbnb data
# -----------------------------------

print("\nStep 1: Cleaning new Airbnb data...")

subprocess.run(
    [
        sys.executable,
        "scripts/1_clean_new_airbnb.py"
    ],
    check=True
)


# -----------------------------------
# Step 2: Combine Airbnb data
# -----------------------------------

print("\nStep 2: Combining Airbnb data...")

subprocess.run(
    [
        sys.executable,
        "scripts/2_combine_airbnb.py"
    ],
    check=True
)


# -----------------------------------
# Step 3: Prepare Airbnb data
# -----------------------------------

print("\nStep 3: Preparing Airbnb data...")

subprocess.run(
    [
        sys.executable,
        "scripts/3_prepare_join.py"
    ],
    check=True
)


# -----------------------------------
# Step 4: Run analyses
# -----------------------------------

print("\nStep 4: Running analyses...")

subprocess.run(
    [
        sys.executable,
        "scripts/4_analyse.py"
    ],
    check=True
)


# -----------------------------------
# Step 5: Create updated plots
# -----------------------------------

print("\nStep 5: Creating updated plots...")

subprocess.run(
    [
        sys.executable,
        "scripts/5_create_plots.py"
    ],
    check=True
)


# -----------------------------------
# Pipeline complete
# -----------------------------------

print("\n===================================")
print("Pipeline completed successfully")
print("===================================")