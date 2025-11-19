library(nflfastR)
library(dplyr)

seasons <- 2025

team_week_adv <- calculate_stats(
  seasons       = seasons,
  summary_level = "week",
  stat_type     = "team",
  season_type   = "REG"
)

write.csv(
  team_week_adv,
  file = "team_week_adv_2025.csv",
  row.names = FALSE
)
