TEAM_NAME_TO_ABBR = {
    "Arizona Cardinals": "ARI",
    "Atlanta Falcons": "ATL",
    "Baltimore Ravens": "BAL",
    "Buffalo Bills": "BUF",
    "Carolina Panthers": "CAR",
    "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN",
    "Cleveland Browns": "CLE",
    "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN",
    "Detroit Lions": "DET",
    "Green Bay Packers": "GB",
    "Houston Texans": "HOU",
    "Indianapolis Colts": "IND",
    "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC",
    "Las Vegas Raiders": "LV",
    "Los Angeles Chargers": "LAC",
    "Los Angeles Rams": "LA",
    "Miami Dolphins": "MIA",
    "Minnesota Vikings": "MIN",
    "New England Patriots": "NE",
    "New Orleans Saints": "NO",
    "New York Giants": "NYG",
    "New York Jets": "NYJ",
    "Philadelphia Eagles": "PHI",
    "Pittsburgh Steelers": "PIT",
    "San Francisco 49ers": "SF",
    "Seattle Seahawks": "SEA",
    "Tampa Bay Buccaneers": "TB",
    "Tennessee Titans": "TEN",
    "Washington Commanders": "WAS",
}

ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"

qb_calculated_stats = [
    "air_yards_per_att",
    "yards_per_att",
    "td_rate",
    "int_rate",
    "fantasy_per_att",
    "delta_attempts",
    "delta_air_yards",
    "delta_cpoe",

    "attempts_3wk_avg",
    "attempts_7wk_avg",
    "attempts_trend_3v7",

    "air_yards_3wk_avg",
    "air_yards_7wk_avg",
    "air_yards_trend_3v7",

    "rush_td_rate",
    "rush_yards_per_game",
    "rush_yards_3wk_avg",
    "rush_yards_7wk_avg",
    "rush_trend_3v7",

    "team_implied_points",
    "pass_defense_rank",
    "pressure_rate_def",

    "fantasy_points",
    "fantasy_3wk_avg",
    "fantasy_7wk_avg",
    "fantasy_trend_3v7",

    "is_rookie",
    "is_second_year",
    "years_exp",
    "draft_number",
    "is_undrafted",
]

rb_calculated_stats = [
    # volume
    "touches",
    "snap_share",
    "rush_share",
    "weighted_opp_share",
    "total_touchdowns",
    "delta_touches",

    # trends
    "touches_3wk_avg",
    "touches_trend_3v7",
    "snap_share_3wk_avg",
    "snap_share_trend_3v7",
    "fantasy_ppr_3wk_avg",
    "fantasy_ppr_trend_3v7",
    "tds_3wk_avg",
    "tds_trend_3v7"

    # rushing efficiency
    "rush_ypc",
    "rush_yards_over_expected_per_att",
    "rush_yoe_per_game",
    "stacked_box_rate",

    # receiving
    "catch_rate",
    "rec_yards_per_target",
    "avg_yac_above_expectation",

    # environment
    "team_implied_points",
    "is_favored",
    "abs_spread",

    # opposing defense
    "def_rush_ypa_allowed",
    "def_rb_carries_allowed",
    "def_rb_receptions_allowed",
    "def_rb_touchdowns_allowed",
    "def_rb_fantasy_points_allowed",

    # profile
    "years_exp_filled",
    "is_rookie",
    "is_undrafted",
    "draft_number_filled",
    ]

wr_te_feature_cols = [
    # volume
    "targets",
    "air_yards",
    "snap_share",
    "target_share",
    "air_yards_share",
    "weighted_opp_share",
    "delta_targets",

    # trends
    "targets_3wk_avg",
    "targets_7wk_avg",
    "targets_trend_3v7",

    "air_yards_3wk_avg",
    "air_yards_7wk_avg",
    "air_yards_trend_3v7",

    "snap_share_3wk_avg",
    "snap_share_trend_3v7",

    "fp_ppr_3wk_avg",
    "fp_ppr_7wk_avg",
    "fp_ppr_trend_3v7",

    # efficiency
    "yards_per_target",
    "rec_td_rate",
    "catch_rate",
    "fp_per_target",

    "avg_intended_air_yards",
    "percent_share_of_intended_air_yards",
    "avg_separation",
    "avg_cushion",
    "avg_yac_above_expectation",
    "racr",

    # environment
    "team_implied_points",
    "is_favored",
    "abs_spread",
    "pass_defense_rank",
    "pressure_rate_def",

    # profile
    "years_exp_filled",
    "is_rookie",
    "is_second_year",
    "is_undrafted",
    "draft_number_filled",
]
