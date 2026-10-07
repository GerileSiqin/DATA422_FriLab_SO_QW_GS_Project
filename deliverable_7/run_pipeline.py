import subprocess
import sys


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
# Step 3: Prepare data for joining
# -----------------------------------

print("\nStep 3: Preparing data for joining...")

subprocess.run(
    [
        sys.executable,
        "scripts/3_prepare_join.py"
    ],
    check=True
)


# -----------------------------------
# Step 4: Join and analyse data
# -----------------------------------

print("\nStep 4: Joining and analysing data...")

subprocess.run(
    [
        sys.executable,
        "scripts/4_analyse.py"
    ],
    check=True
)


# -----------------------------------
# Step 5: Create plot
# -----------------------------------

print("\nStep 5: Creating plot...")

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