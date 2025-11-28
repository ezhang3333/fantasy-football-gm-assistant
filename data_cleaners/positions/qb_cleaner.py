from data_cleaners.nfl_rp_cleaner import NFLReadCleaner
import pandas as pd
import numpy as np
from constants import TEAM_NAME_TO_ABBR

class QBCleaner:
    def __init__(self, cleaned_data, qb_def_stats):
        self.cleaned_data = cleaned_data[cleaned_data["position"] == "QB"].copy()
        self.qb_def_stats = qb_def_stats.copy()

        self.calculated_stats = [
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

    def create_calculated_stats(self):
        df = self.cleaned_data.copy()

        df = df.sort_values(["gsis_id", "week"])

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

        passing_part = 0.04 * df["pass_yards_gained"]
        rushing_part = 0.10 * df["rush_yards_gained"]
        pass_tds     = 4.0  * df["pass_touchdown"]
        rush_tds     = 6.0  * df["rush_touchdown"]
        interceptions = -1.0 * df["pass_interception"]
        fumbles       = -2.0 * df["rush_fumble_lost"]

        df["fantasy_points"] = (
            passing_part
            + rushing_part
            + pass_tds
            + rush_tds
            + interceptions
            + fumbles
        )

        df["fantasy_per_att"] = df["fantasy_points"] / att_safe

        g = df.groupby("gsis_id", group_keys=False)

        df["delta_attempts"] = g["pass_attempt"].diff().fillna(0)
        df["delta_air_yards"] = g["pass_air_yards"].diff().fillna(0)
        df["delta_cpoe"] = g["completion_percentage_above_expectation"].diff().fillna(0)

        df["fantasy_3wk_avg"] = (
            g["fantasy_points"]
            .rolling(window=3, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

        df["fantasy_7wk_avg"] = (
            g["fantasy_points"]
            .rolling(window=7, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

        df["fantasy_trend_3v7"] = df["fantasy_3wk_avg"] - df["fantasy_7wk_avg"]

        df["attempts_3wk_avg"] = (
            g["pass_attempt"]
            .rolling(window=3, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

        df["attempts_7wk_avg"] = (
            g["pass_attempt"]
            .rolling(window=7, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

        df["attempts_trend_3v7"] = df["attempts_3wk_avg"] - df["attempts_7wk_avg"]

        df["air_yards_3wk_avg"] = (
            g["pass_air_yards"]
            .rolling(window=3, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

        df["air_yards_7wk_avg"] = (
            g["pass_air_yards"]
            .rolling(window=7, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

        df["air_yards_trend_3v7"] = df["air_yards_3wk_avg"] - df["air_yards_7wk_avg"]

        rush_att = df["rush_attempt"]
        rush_att_safe = rush_att.clip(lower=1)

        df["rush_td_rate"] = df["rush_touchdown"] / rush_att_safe
        df["rush_yards_per_game"] = df["rush_yards_gained"]

        df["rush_yards_3wk_avg"] = (
            g["rush_yards_gained"]
            .rolling(window=3, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

        df["rush_yards_7wk_avg"] = (
            g["rush_yards_gained"]
            .rolling(window=7, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

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

        qb_def = self.qb_def_stats.rename(columns={"Tm": "opponent"}).copy()
        qb_def["opponent"] = qb_def["opponent"].map(TEAM_NAME_TO_ABBR)

        pressure_rate_median = qb_def["pressure_rate_def"].median()

        df = df.merge(
            qb_def[["opponent", "pass_defense_rank", "pressure_rate_def"]],
            how="left",
            on="opponent",
        )

        df["pass_defense_rank"] = df["pass_defense_rank"].fillna(16.5)
        df["pressure_rate_def"] = df["pressure_rate_def"].fillna(pressure_rate_median)

        df["is_rookie"] = (df["years_exp"] == 0).astype(int)
        df["is_second_year"] = (df["years_exp"] == 1).astype(int)

        df["is_undrafted"] = df["draft_number"].isna().astype(int)
        df["draft_number"] = df["draft_number"].fillna(300).astype(float)

        df["years_exp"] = df["years_exp"].fillna(0).astype(float)

        if hasattr(self, "calculated_stats"):
            cols_to_fill = [c for c in self.calculated_stats if c in df.columns]
            df[cols_to_fill] = df[cols_to_fill].fillna(0)

        self.cleaned_data = df
        return df

