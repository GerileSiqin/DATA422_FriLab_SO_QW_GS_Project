# DATA422_FriLab_SO_QW_GS_Project

DATA422 group project repository for Friday lab

## What we have done so far

1. Created the GitHub repository: DATA422_FriLab_SO_QW_GS_Project.
2. Invited team members and tutors to the repository.
3. Added README.md, .gitignore, and requirements.R.
4. Set up the R + RStudio working environment.
5. Created the Trello board and invited team members.
6. Created a Data Wrangling WhatsApp group for communication.

## Next steps for Deliverable 1

1. Clone the repository onto each team member's computer.
2. Create and edit a simple test file.
3. Practise pull, commit, and push on the main branch.
4. Practise creating branches and pushing to branches.
5. Merge branches back into main.



### How to clone the repository

1. Open our GitHub repository: **DATA422_FriLab_SO_QW_GS_Project.**
2. Click the green **Code** button.
3. Copy the HTTPS link.
4. Open VS Code.
5. Press `Ctrl + Shift + P`.
6. Search for `Git: Clone`.
7. Paste the repository link.
8. Choose a folder on your computer.
9. Click **Open** or **Open in New Window** when VS Code asks.

After cloning, you should see these files:

- README.md
- .gitignore
- requirements.R
- team_guide.md
- DATA422_FriLab_SO_QW_GS_Project.Rproj



## Dataset information

For Deliverable 2, we use the `listings.csv` dataset from Inside Airbnb.

Dataset details:

- Source: Inside Airbnb
- File: `listings.csv`
- Location: New Zealand
- Month: June 2026
- Storage: Stored locally on each team member's computer

The dataset contains information about Airbnb listings in New Zealand.
Each row represents one Airbnb listing.
Each column describes one feature of that listing.

Important columns:

- `id`: unique identifier for each Airbnb listing
- `name`: name of the listing
- `host_id`: unique identifier for the host
- `host_name`: name of the host
- `neighborhood_group`: larger area or district, such as Christchurch
- `neighborhood`: smaller local area of the listing
- `latitude`: north-south coordinate of the listing location
- `longitude`: east-west coordinate of the listing location
- `room_type`: type of accommodation, such as entire apartment or private room
- `price`: price per night stayed
- `minimum_nights`: minimum number of nights required for booking
- `number_of_reviews`: total number of reviews for the listing
- `last_review`: date of the most recent review
- `reviews_per_month`: average number of reviews per month
- `calculated_host_listings_count` -> number of listings associated with the same host
- `availability_365`: number of days the listing is available in the next 365 days
- `number_of_reviews_ltm`: number of reviews in the last twelve months
- `license`: licence or registration information, if available

Note: Column meanings were interpreted using the Inside Airbnb Data Dictionary.

## Project organisation update

The repository has been organised into separate folders for each deliverable to make the project easier to navigate.

### Current folder structure

```text
deliverable_1/
  team_guide.md
  qi_git_practice.md

deliverable_2/
  Airbnb-Christchurch-NZ.ows
  Project-Progress.md
  brave_price_plot.R
```

The main project files remain in the root folder:

```text
README.md
.gitignore
requirements.R
```



### What changed

Deliverable 1 practice files were moved into the `deliverable_1/` folder.

Deliverable 2 workflow and support files were moved into the `deliverable_2/` folder.

The Airbnb dataset file `listings.csv` should still be stored locally on each team member's computer and should not be uploaded to GitHub.

### How to update your local repository

If you already cloned the repository to your computer, you do not need to clone it again.

Open the project folder in RStudio and run these commands in the RStudio Terminal:

```bash
git checkout main
git pull origin main
```

After pulling, your local repository should also show the new folders:

```text
deliverable_1/
deliverable_2/
deliverable_3/
```

## Git Guide for Team Members

Please follow this guide to avoid merge conflicts and accidentally overwriting another teammate’s work.

---

### 1. Why do merge conflicts happen?

A merge conflict can happen when:

- Two people edit the same lines in the same file.
- Several people work directly on the `main` branch.
- Someone starts working without downloading the latest changes.
- A teammate pushes new commits while you are still working.
- Both versions are accepted during a merge, creating duplicated code.

> The best solution is for every teammate to work on a separate branch.

---

### 2. Before starting work

First, make sure your local `main` branch is up to date:

```bash
git switch main
git pull --ff-only origin main



DATA422 Deliverable 6
This folder contains a reviewed and executed revision of the Deliverable 5 comparison pipeline, high-level change notes, a sanity-check demonstration, and AI-assisted design principles. Earlier deliverables and the supplied example-automated-pipeline.zip remain unchanged.

Start with the documents
docs/Design_Principles.docx: editable Word document covering the four required areas and identifying OpenAI ChatGPT through Codex as the AI used.
docs/Coding_Review_and_Sanity_Check.docx: high-level changes and reasons, intentional result changes, and a worked sanity check for the tutor.
Equivalent Markdown versions are stored alongside them.
Inputs and scope
The default inputs are ../deliverable_3/data_processed/christchurch_airbnb_cleaned.csv and ../deliverable_4/bond_data_processed/bond_data_clean_qi.csv. The Airbnb input retains snapshot_date, which the narrower Deliverable 4 Qi listing file drops. The revised pipeline validates prepared data and reproduces enrichment, joining, analysis and export; it does not rebuild the previous raw-data cleaning stages.

inputs/koordinates_coordinate_cache.csv is a byte-preserved copy of the existing Deliverable 5 cache. Offline mode is the default and needs no API key. inputs/source_materials_manifest.json records the reviewed input and reference fingerprints. The supplied lecture supports modularity, descriptive functions, explicit data flow, project-relative paths and scripted changes. The supplied automated-pipeline ZIP demonstrates staged automation, configuration and inspectable outputs.

Reproduce
Use Python 3.14 and an environment with the versions in requirements.txt (the actual analysis versions are also recorded in results/run_manifest.json). The document builder additionally needs python-docx.

From this folder:

python3 -m pip install -r requirements.txt
make
For an existing environment, set make PYTHON=/path/to/python. If document generation uses a separate environment, set DOCUMENT_PYTHON=/path/to/document/python. make runs the full analysis, saved-output sanity demonstration, regression and edge-test verification, and Word and Markdown document generation. It deliberately rebuilds the workflow; it does not implement per-stage incremental builds. R and Quarto are unnecessary for this Python implementation.

Run individual stages:

python3 run_pipeline.py
python3 sanity_check_example.py
python3 -m unittest discover -s tests -v
python3 tools/verify_delivery.py
python3 tools/build_documents.py
For different inputs:

python3 run_pipeline.py --airbnb /path/listings.csv --bonds /path/bonds.csv \
  --cache /path/cache.csv --output /path/new_results
Only the pipeline and sanity script support alternative result directories. The delivered document builder and regression verifier intentionally use this folder's results and the supplied June 2026 baseline; they need adapting before being used as verification of another dataset. One snapshot per quarter is required. config.json changes worker count and the observed-gap minimum; both also have command-line overrides.

New SA2 queries require --allow-network and KOORDINATES_API_KEY in the environment. The current package was verified offline. A failed live run retains its checkpoint; resume by passing that checkpoint as --cache and selecting a new --output folder. Input files cannot be located inside the selected output folder.

Verified results and intentional corrections
3,469 listings retained; 3,469 SA2 matches; 2,673 bond records and rents matched; 2,474 usable listing gaps; 274 missing prices retained.
174 SA2 groups. All prior joined values and location statistics match Deliverable 5 within numeric tolerance.
10 analytical checks and 19 adversarial tests passed; all six SQLite tables match their CSV contents.
Gap ranking now requires five observed price gaps, rather than five total listings. Four locations leave the eligible set (95 to 91), including the previous leader Bryndwr South, which has only four priced listings.
Wigram North and Holmwood share the highest eligible gap rounded to cents, NZ$242.71. Christchurch Central remains NZ$250.00 median/night, from 117 priced listings among 119 total listings.
Package map
run_pipeline.py orchestrates the stages in pipeline/. tests/ contains edge tests. sanity_check_example.py verifies saved outputs and hand-checks one listing. tools/verify_delivery.py independently checks exports and baseline agreement. tools/build_documents.py generates the Word and Markdown documents from verified evidence.

results/data_processed/ contains six CSV tables; results/deliverable_6.sqlite contains the same tables. Plots, automatically generated analysis notes, quality checks, a run manifest, the persisted sanity example, the test log and delivery verification report are in results/. _SUCCESS.json marks successful completion of the analytical pipeline, not of document rendering or every later verification stage.

The geographic cache is inherited evidence, not a fresh API or polygon check. Bond SA2 vintage compatibility is unresolved from the available files. Active bonds and Airbnb listings have different definitions; missing bond data is not zero. The reported price gap is descriptive and does not establish causation or returns.
