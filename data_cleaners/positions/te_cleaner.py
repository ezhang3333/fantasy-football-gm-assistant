import numpy as np
from constants import te_calculated_stats

class TECleaner:
    def __init__(self, merged_data, te_def_stats):
        self.merged_data = merged_data[merged_data["position"] == "TE"].copy()
        self.te_def_stats = te_def_stats.copy()
        self.calculated_stats = te_calculated_stats

    def add_calculated_stats(self):
        df = self.merged_data.copy()

        zero_fill_cols = [
            "rush_yards_gained",
            "rec_yards_gained",
            "pass_yards_gained",
            "rush_touchdown",
            "rec_touchdown",
            "pass_touchdown",
            "rec_fumble_lost",
            "rush_fumble_lost",
            "rec_attempt",
            "pass_air_yards",
            "offense_pct",
            "rec_attempt_team",
            "rush_attempt",
            "rush_attempt_team",
            "receptions",
            "rec_air_yards",
            "rush_touchdown",
            "rec_touchdown", 
            "percent_share_of_intended_air_yards",
            "avg_separation",
            "avg_cushion",
            "avg_yac_above_expectation"           
        ]

        for col in zero_fill_cols:
            if col in df:
                df[col] = df[col].fillna(0)
        
        # receiving volume
        df["targets"] = df["rec_attempt"]
        df["air_yards"] = df["rec_air_yards"]
        df["snap_share"] = df["offense_pct"]
        df["target_share"] = df["rec_attempt"] / df["rec_attempt_team"]
        df["air_yards_share"] = df["percent_share_of_intended_air_yards"]
        df["total_touchdowns"] = df["rush_touchdown"] + df["rec_touchdown"]

        df["fantasy_points"] = (
            0.1 * df["rush_yards_gained"] + 
            0.1 * df["rec_yards_gained"] + 
            0.04 * df["pass_yards_gained"] + 
            6.0 * df["rush_touchdown"] + 
            6.0 * df["rec_touchdown"] + 
            4.0 * df["pass_touchdown"] + 
            1.0 * df["receptions"] -
            2.0 * df["rec_fumble_lost"] - 
            2.0 * df["rush_fumble_lost"] + 
            # bonuses
            3.0 * (df["rush_yards_gained"] >= 100) + 
            3.0 * (df["rush_yards_gained"] >= 200) +
            3.0 * (df["rec_yards_gained"] >= 100) + 
            3.0 * (df["rec_yards_gained"] >= 200) 
        )

        # rushing volume
        df["rush_attempts"] = df["rush_attempt"]
        df["rush_ypa"] = df["rush_yards_gained"] / df["rush_attempt"]
        df["rush_share"] = df["rush_attempt"] / df["rush_attempt_team"]

        df_sorted = df.sort_values(["gsis_id", "week"]) 
        grouped_player_df = df_sorted.groupby("gsis_id")

        df["delta_targets"] = grouped_player_df["targets"].diff(periods=1)

        # trends
        df["targets_3wk_avg"] = grouped_player_df["targets"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        df["targets_7wk_avg"] = grouped_player_df["targets"].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
        df["targets_trend_3v7"] = df["targets_3wk_avg"] - df["targets_7wk_avg"]

        df["air_yards_3wk_avg"] = grouped_player_df["rec_air_yards"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        df["air_yards_7wk_avg"] = grouped_player_df["rec_air_yards"].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
        df["air_yards_trend_3v7"] = df["air_yards_3wk_avg"] - df["air_yards_7wk_avg"]
        

        df["snap_share_3wk_avg"] = grouped_player_df["snap_share"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        df["snap_share_7wk_avg"] = grouped_player_df["snap_share"].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
        df["snap_share_trend_3v7"] = df["snap_share_3wk_avg"] - df["snap_share_7wk_avg"]

        df["fantasy_ppr_3wk_avg"] = grouped_player_df["fantasy_points"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        df["fantasy_ppr_7wk_avg"] = grouped_player_df["fantasy_points"].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
        df["fantasy_ppr_trend_3v7"] = df["fantasy_ppr_3wk_avg"] - df["fantasy_ppr_7wk_avg"]

        df["tds_3wk_avg"] = grouped_player_df["total_touchdowns"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        df["tds_7wk_avg"] = grouped_player_df["total_touchdowns"].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
        df["tds_trend_3v7"] = df["tds_3wk_avg"] - df["tds_7wk_avg"]

        df["gadget_usage_3wk_avg"] = grouped_player_df["rush_attempt"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)

        # efficiency
        df["yards_per_target"] = df["rec_yards_gained"] / df["rec_attempt"]
        df["rec_td_rate"] = df["rec_touchdown"] / df["receptions"]
        df["catch_rate"] = df["receptions"] / df["rec_attempt"]
        df["fp_per_target"] = df["fantasy_points"] / df["rec_attempt"]
        df["racr"] = df["rec_yards_gained"] / df["air_yards"]

        # environment
        is_home = df["team"] == df["team_home"]
        home_implied = df["total"] / 2.0 - df["spread_line"] / 2.0
        away_implied = df["total"] / 2.0 + df["spread_line"] / 2.0

        df["team_implied_points"] = np.where(
            df["team"] == df["team_home"],
            home_implied,
            away_implied,
        )
        team_spread = np.where(is_home, df["spread_line"], -df["spread_line"])
        df["is_favored"] = (team_spread < 0).astype(int)
        df["abs_spread"] = np.abs(team_spread)

        # opposing defense
        def_te_stats = self.te_def_stats.set_index("team_abbrev")
        df = df.merge(def_te_stats, left_on="team_away", right_index=True, how="left")

        # profile
        df["years_exp_filled"] = df["years_exp"].fillna(0)
        df["is_rookie"] = (df["years_exp"] == 0).astype(int)
        df["is_second_year"] = (df["years_exp"] == 0).astype(int)
        df["draft_number_filled"] = df["draft_number"].fillna(275)
        df["is_undrafted"] = (df["draft_number_filled"] == 275).astype(int)

        post_division_zero_fill_cols = [
            "delta_targets",
            "target_share",
            "rush_ypa",
            "rush_share",
            "yards_per_target",
            "rec_td_rate",
            "catch_rate",
            "fp_per_target",
            "racr"
        ]

        for col in post_division_zero_fill_cols:
            if col in df:
                df[col] = df[col].fillna(0)

        return df