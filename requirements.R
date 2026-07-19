# DATA422 project requirements
# This script checks and installs the R packages needed for the project.

required_packages <- c(
  "tidyverse",
  "readxl",
  "writexl",
  "DBI",
  "RSQLite"
)

missing_packages <- required_packages[
  !required_packages %in% rownames(installed.packages())
]

install.packages(missing_packages)
