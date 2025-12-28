import pandas as pd

class NFLReadCleaner:
    def __init__(self, raw_data):
        self.raw_data = raw_data.copy()
        
        self.keep = {
            'rosters_weekly' : [
                'season', 'team', 'position', 'full_name', 'height', 'weight', 'gsis_id', 'years_exp',
                'week', 'draft_number'
            ],
            'schedules' : [
                'season', 'week', 'home_team', 'away_team', 'total', 'spread_line', 'roof', 'surface', 'temp', 'wind'
            ],
            'snap_counts' : [
                'season', 'week', 'player', 'position', 'team', 'opponent', 'offense_snaps', 'offense_pct'
            ],
            'nextgen_stats' : [
                'season', 'week', 'avg_time_to_throw', 'avg_intended_air_yards', 'aggressiveness', 'avg_air_yards_to_sticks',
                'completion_percentage_above_expectation', 'max_air_distance', 'efficiency',
                'percent_attempts_gte_eight_defenders', 'rush_yards', 'rush_yards_over_expected_per_att', 
                'avg_cushion', 'avg_separation', 'percent_share_of_intended_air_yards','catch_percentage',
                'avg_yac_above_expectation','player_gsis_id'
            ],
            'ff_opportunity' : [
                'season', 'player_id', 'week', 'pass_attempt', 'rec_attempt', 'rush_attempt', 'pass_air_yards', 'rec_air_yards',
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
        for name, dataset in cleaned.items():
            if "season" in dataset.columns and "week" in dataset.columns:
                cleaned[name] = self.drop_playoff_weeks(dataset)

        merged = cleaned['rosters_weekly']
        merged = pd.merge(
            merged,
            cleaned['nextgen_stats'],
            left_on=['gsis_id', 'week', 'season'],
            right_on=['player_gsis_id', 'week', 'season'],
            how='left'
        )
        merged = pd.merge(
            merged,
            cleaned['ff_opportunity'],
            left_on=['gsis_id', 'week', 'season'],
            right_on=['player_id', 'week', 'season'],
            how='left'
        )
        merged = pd.merge(
            merged,
            cleaned['snap_counts'],
            left_on=['season', 'team', 'position', 'full_name', 'week'],
            right_on=['season', 'team', 'position', 'player', 'week'],
            how='left'
        )
        schedules = cleaned['schedules'].rename(columns={
            'home_team': 'team_home',
            'away_team': 'team_away'
        })
        home_merge = pd.merge(
            merged,
            schedules,
            left_on=['season', 'team', 'week'],
            right_on=['season', 'team_home', 'week'],
            how='left'
        )
        away_merge = pd.merge(
            merged,
            schedules,
            left_on=['season', 'team', 'week'],
            right_on=['season', 'team_away', 'week'],
            how='left'
        )
        merged = home_merge.combine_first(away_merge)
        merged = merged.drop(columns=['player_id', 'player_gsis_id', 'player'], errors='ignore')
        return merged

    def max_reg_week(self, season):
        if pd.isna(season):
            return 18
        season = int(season)
        if season >= 2021:
            return 18
        if season >= 1990:
            return 17
        return 16

    def drop_playoff_weeks(self, df):
        df = df.copy()
        
        df["season"] = pd.to_numeric(df["season"], errors="coerce")
        df["week"] = pd.to_numeric(df["week"], errors="coerce")
        df["max_week"] = df["season"].apply(self.max_reg_week)
        df = df[df["week"] <= df["max_week"]]
        df = df.drop(columns=["max_week"])
        return df