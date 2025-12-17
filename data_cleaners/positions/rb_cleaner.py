import pandas as pd
import numpy as np
from constants import rb_calculated_stats

class RBCleaner:
    def __init__(self, merged_data, rb_def_stats):
        self.merged_data = merged_data[merged_data["position"] == "RB"].copy()
        self.rb_def_stats = rb_def_stats.copy()
        self.calculated_stats = rb_calculated_stats

    def add_calculated_stats(self):
        df = self.merged_data.copy()

        zero_fill_cols = [
            "rec_attempt",
            "rush_attempt",
            "offense_pct",
            "rush_touchdown",
            "rec_touchdown",
            "rush_yards_gained",
            "rec_yards_gained",
            "pass_yards_gained",
            "pass_touchdown",
            "receptions",
            "rec_fumble_lost",
            "rush_fumble_lost",
            "rush_yards_over_expected_per_att",
            "percent_attempts_gte_eight_defenders",
            "avg_yac_above_expectation"
        ]

        for col in zero_fill_cols:
            if col in df:
                df[col] = df[col].fillna(0)
        
        # volume
        df["touches"] = df["rec_attempt"] + df["rush_attempt"]
        df["snap_share"] = df["offense_pct"]
        df["target_share"] = df["rec_attempt"] / df["rec_attempt_team"]
        df["rush_share"] = df["rush_attempt"] / df["rush_attempt_team"]
        df["weighted_opp_share"] = df["rush_attempt"] + 3 * df["rec_attempt"]
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

        df_sorted = df.sort_values(["gsis_id", "week"]) 
        grouped_player_df = df_sorted.groupby("gsis_id")

        df["delta_touches"] = grouped_player_df["touches"].diff(periods=1)

        # trends
        df["touches_3wk_avg"] = grouped_player_df["touches"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        df["touches_7wk_avg"] = grouped_player_df["touches"].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
        df["touches_trend_3v7"] = df["touches_3wk_avg"] - df["touches_7wk_avg"]

        df["snap_share_3wk_avg"] = grouped_player_df["snap_share"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        df["snap_share_7wk_avg"] = grouped_player_df["snap_share"].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
        df["snap_share_trend_3v7"] = df["snap_share_3wk_avg"] - df["snap_share_7wk_avg"]

        df["fantasy_ppr_3wk_avg"] = grouped_player_df["fantasy_points"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        df["fantasy_ppr_7wk_avg"] = grouped_player_df["fantasy_points"].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
        df["fantasy_ppr_trend_3v7"] = df["fantasy_ppr_3wk_avg"] - df["fantasy_ppr_7wk_avg"]

        df["tds_3wk_avg"] = grouped_player_df["total_touchdowns"].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)
        df["tds_7wk_avg"] = grouped_player_df["total_touchdowns"].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
        df["tds_trend_3v7"] = df["tds_3wk_avg"] - df["tds_7wk_avg"]

        # rushing efficiency
        df["rush_ypc"] = df["rush_yards_gained"] / df["rush_attempt"]
        df["rush_yoe_per_game"] = df["rush_yards_over_expected_per_att"] * df["rush_attempt"]
        df["rush_yoe_per_att"] = df["rush_yards_over_expected_per_att"]
        df["stacked_box_rate"] = df["percent_attempts_gte_eight_defenders"]

        # receiving
        df["catch_rate"] = df["receptions"] / df["rec_attempt"]
        df["rec_yards_per_target"] = df["rec_yards_gained"] / df["rec_attempt"]

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
        def_rb_stats = self.rb_def_stats.set_index("team_abbrev")
        df = df.merge(def_rb_stats, left_on="team_away", right_index=True, how="left")

        # profile
        df["years_exp_filled"] = df["years_exp"].fillna(0)
        df["is_rookie"] = (df["years_exp"] == 0).astype(int)
        df["draft_number_filled"] = df["draft_number"].fillna(275)
        df["is_undrafted"] = (df["draft_number_filled"] == 275).astype(int)

        post_division_zero_fill_cols = [
            "rush_ypc",
            "catch_rate",
            "rec_yards_per_target",
            "delta_touches",
            "rush_share",
            "target_share"
        ]

        for col in post_division_zero_fill_cols:
            if col in df:
                df[col] = df[col].fillna(0)

        return df