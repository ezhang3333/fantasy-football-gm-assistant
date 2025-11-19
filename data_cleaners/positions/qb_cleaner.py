from data_cleaners.nfl_rp_cleaner import NFLReadCleaner
import pandas as pd
import numpy as np

class QBCleaner:
    def _init__(self, cleaned_data):
        self.cleaned_data = cleaned_data[cleaned_data['position'] == 'QB'].copy()
        
        # just here to display the calculated stats
        self.calculated_stats = [
            'air_yards_per_att',
            'yards_per_att',
            'td_rate',
            'int_rate',
            'fantasy_per_att',
            'delta_attempts',
            'delta_air_yards',
            'delta_cpoe',
            'attempts_3wk_avg',
            'air_yards_3wk_avg',
            'fantasy_3wk_avg',
            'rush_td_rate',
            'rush_yards_per_game',
            'team_implied_points',
            'opponent_pass_def_rank'
        ]
    
    def create_calculated_stats(self) -> pd.DataFrame:
        df = self.cleaned_data
        df = df.sort_values(["gsis_id", "week"])

        att = df["pass_attempt"].fillna(0)
        att_safe = att.clip(lower=1)

        df["air_yards_per_att"] = df["pass_air_yards"].fillna(0) / att_safe
        df["yards_per_att"] = df["pass_yards_gained"].fillna(0) / att_safe
        df["td_rate"] = df["pass_touchdown"].fillna(0) / att_safe
        df["int_rate"] = df["pass_interception"].fillna(0) / att_safe

        fantasy_raw = (
            df["pass_yards_gained"].fillna(0) / 25.0
            + df["pass_touchdown"].fillna(0) * 4.0
            - df["pass_interception"].fillna(0) * 2.0
        )
        df["fantasy_per_att"] = fantasy_raw / att_safe

        g = df.groupby("gsis_id", group_keys=False)

        df["delta_attempts"] = g["pass_attempt"].diff()
        df["delta_air_yards"] = g["pass_air_yards"].diff()
        df["delta_cpoe"] = g["completion_percentage_above_expectation"].diff()

        # past 3 weeks
        df["attempts_3wk_avg"] = g["pass_attempt"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        df["air_yards_3wk_avg"] = g["pass_air_yards"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)

        rush_att_safe = df["rush_attempt"].fillna(0).clip(lower=1)
        df["rush_td_rate"] = df["rush_touchdown"].fillna(0) / rush_att_safe
        df["rush_yards_per_game"] = df["rush_yards_gained"].fillna(0)


        # home implied = total/2 - spread/2 ; away implied = total/2 + spread/2
        total = df["total"].astype(float)
        spread = df["spread_line"].astype(float)

        home_implied = total / 2.0 - spread / 2.0
        away_implied = total / 2.0 + spread / 2.0

        df["team_implied_points"] = np.where(
            df["team"] == df["home_team"],
            home_implied,
            away_implied,
        )

        # need to add some feature about opponent defense and fantasy points and rolling 3 week average for fantasy points

        self.cleaned_data = df
        return df

    def calculate_fantasy_points(passing_yards, rushing_yards, passing_touchdowns, rushing_touchdowns, interceptions, fumbles):
        return (
                0.04 * passing_yards 
                + 0.1 * rushing_yards 
                + 4 * passing_touchdowns 
                + 6 * rushing_touchdowns 
                - interceptions 
                - 2 * fumbles
            )

    


# add trendy stats like past 5 weeks usage and target share or like past 3 weeks, decide the number of weeks later        
"""
 THESE ARE INDENTIFIERS: 'team', 'position', 'full_name', 'gsis_id', 'week'
 NEED TO ENCODE THESE: 'roof', 'surface'

air_yards_per_att
yards_per_att
td_rate
int_rate
fantasy_per_att
delta_attempts
delta_air_yards
delta_cpoe
attempts_3wk_avg
air_yards_3wk_avg
fantasy_3wk_avg
rush_td_rate
rush_yards_per_game
team_implied_points
opponent_pass_def_rank

 RAW FEATURES: 'height', 'weight', 'years_exp', 'draft_number', 'total', 'spread_line', 'temp', 'wind',
'avg_time_to_throw', 'avg_intended_air_yards', 'aggressiveness', 'avg_air_yards_to_sticks',
'completion_percentage_above_expectation', 'max_air_distance', 'pass_attempt', 'pass_air_yards', 'pass_yards_gained
'pass_touchdown', 'rush_touchdown', 'pass_interception', 'pass_touchdown_diff', ''
"""