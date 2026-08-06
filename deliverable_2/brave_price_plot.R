library(tidyverse)

listings <- read_csv(file.choose())

listings_clean <- listings |>
  filter(!is.na(price)) |>
  filter(price <= 1000)

all_nz <- listings_clean |>
  mutate(group = "All New Zealand")

christchurch <- listings_clean |>
  filter(neighbourhood_group == "Christchurch City") |>
  mutate(group = "Christchurch City")

plot_data <- bind_rows(all_nz, christchurch)

ggplot(plot_data, aes(x = price, fill = group)) +
  geom_histogram(
    aes(y = after_stat(density)), 
    binwidth = 50,
    alpha = 0.5,
    position = "identity"
  ) +
  labs(
    title = "Price Distribution of Airbnb Listings",
    subtitle = "All New Zealand compared with Christchurch City",
    x = "Price per night",
    y = "Density",
    fill = "Group"
  ) + 
  theme_minimal()
