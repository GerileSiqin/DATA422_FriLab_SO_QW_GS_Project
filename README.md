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
```
