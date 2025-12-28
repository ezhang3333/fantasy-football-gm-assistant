import pandas as pd
import numpy as np
from constants import TEAM_NAME_TO_ABBR, qb_calculated_stats

class QBCleaner:
    def __init__(self, merged_data, qb_def_stats):
        self.merged_data = merged_data[merged_data["position"] == "QB"].copy()
        self.qb_def_stats = qb_def_stats.copy()
        self.calculated_stats = qb_calculated_stats

    def add_calculated_stats(self):
        df = self.merged_data.copy()
        df = df.sort_values(["gsis_id", "week", "season"]).reset_index(drop=True)

        zero_fill_cols = [
            "pass_attempt",
            "pass_air_yards",
            "pass_yards_gained",
            "pass_touchdown",
            "pass_interception",
            "rush_yards_gained",
            "rush_fumble_lost",
            "rush_attempt",
            "rush_touchdown",
            "completion_percentage_above_expectation",
            "rec_yards_gained",
            "rec_touchdown",
            "rec_fumble_lost"
        ]

        for col in zero_fill_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0)

        if "total" in df.columns:
            df["total"] = df["total"].astype(float).fillna(0)
        if "spread_line" in df.columns:
            df["spread_line"] = df["spread_line"].astype(float).fillna(0)

        att = df["pass_attempt"]
        att_safe = att.clip(lower=1)

        df["air_yards_per_att"] = df["pass_air_yards"] / att_safe
        df["yards_per_att"] = df["pass_yards_gained"] / att_safe
        df["td_rate"] = df["pass_touchdown"] / att_safe
        df["int_rate"] = df["pass_interception"] / att_safe

        df["fantasy_points"] = (
            0.04 * df["pass_yards_gained"]
            + 0.10 * df["rush_yards_gained"]
            + 0.10 * df["rec_yards_gained"]
            + 4.0 * df["pass_touchdown"]
            + 6.0 * df["rush_touchdown"]
            + 6.0 * df["rec_touchdown"]
            - 1.0 * df["pass_interception"]
            - 2.0 * df["rush_fumble_lost"]
            - 2.0 * df["rec_fumble_lost"]
            # bonuses
            + 3.0 * (df["rush_yards_gained"] >= 100)
            + 3.0 * (df["rush_yards_gained"] >= 200)
            + 3.0 * (df["pass_yards_gained"] >= 300)
            + 3.0 * (df["pass_yards_gained"] >= 400)
        )

        df["fantasy_per_att"] = df["fantasy_points"] / att_safe

        g = df.groupby(["gsis_id", "season"], group_keys=False)

        df["delta_attempts"] = g["pass_attempt"].diff().fillna(0)
        df["delta_air_yards"] = g["pass_air_yards"].diff().fillna(0)
        df["delta_cpoe"] = g["completion_percentage_above_expectation"].diff().fillna(0)

        df["fantasy_3wk_avg"] = g["fantasy_points"].rolling(window=3, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        df["fantasy_7wk_avg"] = g["fantasy_points"].rolling(window=7, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        df["fantasy_trend_3v7"] = df["fantasy_3wk_avg"] - df["fantasy_7wk_avg"]
        shifted_fantasy_points = g["fantasy_points"].shift(1)
        df["fantasy_prev_5wk_avg"] = (
            shifted_fantasy_points.groupby([df["gsis_id"], df["season"]], sort=False)
            .rolling(window=5, min_periods=1)
            .mean()
            .reset_index(level=[0, 1], drop=True)
        )

        df["attempts_3wk_avg"] = g["pass_attempt"].rolling(window=3, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        df["attempts_7wk_avg"] = g["pass_attempt"].rolling(window=7, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        df["attempts_trend_3v7"] = df["attempts_3wk_avg"] - df["attempts_7wk_avg"]

        df["air_yards_3wk_avg"] = g["pass_air_yards"].rolling(window=3, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        df["air_yards_7wk_avg"] = g["pass_air_yards"].rolling(window=7, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        df["air_yards_trend_3v7"] = df["air_yards_3wk_avg"] - df["air_yards_7wk_avg"]

        rush_att = df["rush_attempt"]
        rush_att_safe = rush_att.clip(lower=1)

        df["rush_td_rate"] = df["rush_touchdown"] / rush_att_safe
        df["rush_yards_per_game"] = df["rush_yards_gained"]

        df["rush_yards_3wk_avg"] = g["rush_yards_gained"].rolling(window=3, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        df["rush_yards_7wk_avg"] = g["rush_yards_gained"].rolling(window=7, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        df["rush_trend_3v7"] = df["rush_yards_3wk_avg"] - df["rush_yards_7wk_avg"]

        total = df["total"]
        spread = df["spread_line"]

        home_implied = total / 2.0 - spread / 2.0
        away_implied = total / 2.0 + spread / 2.0

        df["team_implied_points"] = np.where(
            df["team"] == df["team_home"],
            home_implied,
            away_implied,
        )

        df["opp_team"] = np.where(df["team"] == df["team_home"], df["team_away"], df["team_home"])
        df = df.merge(
            self.qb_def_stats,
            left_on=["season", "opp_team"],
            right_on=["season", "team_abbrev"],
            how="left"
        ).drop(columns=["team_abbrev", "opp_team"], errors="ignore")

        df["is_rookie"] = (df["years_exp"] == 0).astype(int)
        df["is_second_year"] = (df["years_exp"] == 1).astype(int)

        df["is_undrafted"] = df["draft_number"].isna().astype(int)
        df["draft_number"] = df["draft_number"].fillna(275).astype(float)

        df["years_exp"] = df["years_exp"].fillna(0).astype(float)

        if hasattr(self, "calculated_stats"):
            cols_to_fill = [c for c in self.calculated_stats if c in df.columns]
            df[cols_to_fill] = df[cols_to_fill].fillna(0)

        return df

