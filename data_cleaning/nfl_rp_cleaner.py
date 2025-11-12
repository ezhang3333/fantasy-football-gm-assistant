from data_extractors.nfl_rp_extractor import NFLReadExtractor

class NFLReadCleaner:
    def __init__(self, extracted_data):
        self.raw_data = extracted_data

    def merge_data_to_player_weeks():
        # ignore player_stats and team_stats and players and rosters because they are season based
        # roster_weekly: team, position, full name, height, weight, years in league, draft number, gsis id
        # schedules: week, home team, away team, total, spread line, roof, surface, temp, wind
        # snap_counts: week, player, oppoonent, offense_snaps, offense_pct
        # nextgen_stats: week, player, avg_time_to_throw,  
        # Team situation: 
        return None

    def fill_missing_values():
        return None

    def add_calculated_features():
        return None

    def build_final_data():
        return None

"week", "avg_time_to_throw","avg_intended_air_yards",
"aggressiveness","avg_air_yards_to_sticks", "completion_percentage_above_expectation", 
"max_air_distance", "efficiency","percent_attempts_gte_eight_defenders", "rush_yards",
"rush_yards_over_expected_per_att", "avg_cushion", "avg_separation",
"percent_share_of_intended_air_yards", "catch_percentage",
"avg_yac_above_expectation","player_gsis_id"

"pass_attempt","rec_attempt","rush_attempt",
"pass_air_yards","rec_air_yards",
"pass_completions","receptions",
"pass_yards_gained","rec_yards_gained","rush_yards_gained",
"pass_touchdown","rec_touchdown","rush_touchdown",
"pass_interception",
"rec_fumble_lost","rush_fumble_lost",
"pass_yards_gained_diff","rec_yards_gained_diff","rush_yards_gained_diff",
"pass_touchdown_diff","rec_touchdown_diff","rush_touchdown_diff",
"pass_attempt_team","rec_attempt_team","rush_attempt_team",


# add trendy stats like past 5 weeks usage and target share or like past 3 weeks, decide the number of weeks later