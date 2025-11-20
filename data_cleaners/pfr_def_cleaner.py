
import pandas as pd
import numpy as np

class PFRDefCleaner:
    def __init__(self, team_def_stats, adv_def_stats):
        self.year = 2025
        self.team_def_stats = team_def_stats
        self.adv_def_stats = adv_def_stats

        self.calculate_stats = {
            'team_def_stats' : [
                'Tm', 'G', 'PA', 'NY/A'
            ],
            'adv_def_stats' : [
                'Tm', 'G', 'Att', 'Yds', 'TD', 'Prss%'
            ]
        }
    
    def calculate_qb_def_stats(self):
        team = self.team_def_stats[self.calculate_stats["team_def_stats"]].copy()
        adv  = self.adv_def_stats[self.calculate_stats["adv_def_stats"]].copy()

        team = team.rename(columns={"G": "G_team"})
        adv = adv.rename(columns={"G": "G_adv"})

        for col in ["G_team", "PA", "NY/A"]:
            team[col] = pd.to_numeric(team[col], errors="coerce")

        for col in ["G_adv", "Att", "Yds", "TD", "Prss%"]:
            adv[col] = pd.to_numeric(adv[col], errors="coerce")

        df = pd.merge(team, adv, on="Tm", how="inner")

        df["def_points_per_game"] = df["PA"] / df["G_team"].clip(lower=1)

        att_safe = df["Att"].fillna(0).clip(lower=1)
        df["def_pass_yds_per_att"] = df["Yds"].fillna(0) / att_safe

        df["def_pass_td_rate"] = df["TD"].fillna(0) / att_safe

        df["def_pass_nya"] = df["NY/A"]

        df["def_pressure_rate"] = df["Prss%"]


        yds_rank = df["def_pass_yds_per_att"].rank(ascending=True, method="average")
        td_rank  = df["def_pass_td_rate"].rank(ascending=True, method="average")
        prs_rank = df["def_pressure_rate"].rank(ascending=False, method="average")
        pts_rank = df["def_points_per_game"].rank(ascending=True, method="average")

        composite = (
            0.4 * yds_rank +
            0.3 * td_rank +
            0.2 * prs_rank +
            0.1 * pts_rank
        )

        df["opponent_pass_def_rank"] = composite.rank(ascending=True, method="dense")

        qb_def = df[[
            "Tm",
            "def_points_per_game",
            "def_pass_yds_per_att",
            "def_pass_td_rate",
            "def_pass_nya",
            "def_pressure_rate",
            "opponent_pass_def_rank",
        ]].copy()

        return qb_def
    
