from data_extractors.nfl_rp_extractor import NFLReadExtractor
import pandas as pd

class NFLReadCleaner:
    def __init__(self, extracted_data):
        self.raw_data = extracted_data.copy()
        
        self.keep = {
            'rosters_weekly' : [
                'team', 'position', 'full_name', 'height', 'weight', 'gsis_id', 'years_exp', 
                'week', 'draft_number'
            ],
            'schedules' : [
                'week', 'home_team', 'away_team', 'total', 'spread_line', 'roof', 'surface', 'temp', 'wind'
            ],
            'snap_counts' : [
                'week', 'player', 'position', 'team', 'opponent', 'offense_snaps', 'offense_pct'
            ],
            'nextgen_stats' : [
                'season', 'week', 'avg_time_to_throw', 'avg_intended_air_yards', 'aggressiveness', 'avg_air_yards_to_sticks',
                'completion_percentage_above_expectation', 'max_air_distance', 'efficiency',
                'percent_attempts_gte_eight_defenders', 'rush_yards', 'rush_yards_over_expected_per_att', 
                'avg_cushion', 'avg_separation', 'percent_share_of_intended_air_yards','catch_percentage',
                'avg_yac_above_expectation','player_gsis_id'
            ],
            'ff_opportunity' : [
                'player_id', 'week', 'pass_attempt', 'rec_attempt', 'rush_attempt', 'pass_air_yards', 'rec_air_yards',
                'pass_completions', 'receptions', 'pass_yards_gained', 'rec_yards_gained', 'rush_yards_gained',
                'pass_touchdown', 'rec_touchdown', 'rush_touchdown', 'pass_interception', 'rec_fumble_lost', 
                'rush_fumble_lost', 'pass_yards_gained_diff', 'rec_yards_gained_diff', 'rush_yards_gained_diff', 
                'pass_touchdown_diff', 'rec_touchdown_diff', 'rush_touchdown_diff', 'pass_attempt_team', 
                'rec_attempt_team', 'rush_attempt_team' 
            ]
        }   

    def merge_data_to_player_weeks(self):
        cleaned = {}
        for dataset_name, dataset_columns in self.keep.items():
            cleaned[dataset_name] = self.raw_data[dataset_name].reindex(columns=dataset_columns)
        merged = cleaned['rosters_weekly']

        merged = pd.merge(
            merged,
            cleaned['nextgen_stats'],
            left_on=['gsis_id', 'week'],
            right_on=['player_gsis_id', 'week'],
            how='left'
        )

        merged = pd.merge(
            merged,
            cleaned['ff_opportunity'],
            left_on=['gsis_id', 'week'],
            right_on=['player_id', 'week'],
            how='left'
        )

        merged = pd.merge(
            merged,
            cleaned['snap_counts'],
            left_on=['team', 'position', 'full_name', 'week'],
            right_on=['team', 'position', 'player', 'week'],
            how='left'
        )

        schedules = cleaned['schedules'].rename(columns={
            'home_team': 'team_home',
            'away_team': 'team_away'
        })

        home_merge = pd.merge(
            merged,
            schedules,
            left_on=['team', 'week'],
            right_on=['team_home', 'week'],
            how='left'
        )

        away_merge = pd.merge(
            merged,
            schedules,
            left_on=['team', 'week'],
            right_on=['team_away', 'week'],
            how='left'
        )

        merged = home_merge.combine_first(away_merge)
        merged = merged.drop(columns=['player_id', 'player_gsis_id', 'player'], errors='ignore')
        return merged