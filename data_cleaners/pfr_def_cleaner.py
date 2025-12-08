from services.espn_api import get_current_season
import pandas as pd
import numpy as np

class PFRDefCleaner:
    def __init__(self, team_def_stats, adv_def_stats):
        self.year = get_current_season()
        self.team_def_stats = team_def_stats.copy()
        self.adv_def_stats = adv_def_stats.copy()

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
        adv["Prss%"] = adv["Prss%"].astype(str).str.replace("%", "", regex=False)

        team = team.rename(columns={"G": "G_team"})
        adv = adv.rename(columns={"G": "G_adv"})

        for col in ["G_team", "PA", "NY/A"]:
            team[col] = pd.to_numeric(team[col], errors="coerce")

        for col in ["G_adv", "Att", "Yds", "TD", "Prss%"]:
            adv[col] = pd.to_numeric(adv[col], errors="coerce")

        df = pd.merge(team, adv, on="Tm", how="inner")

        df["pts_allowed_per_game"] = df["PA"] / df["G_team"].clip(lower=1)

        att_safe = df["Att"].fillna(0).clip(lower=1)
        df["pass_yds_allowed_per_att"] = df["Yds"].fillna(0) / att_safe
        df["pass_td_rate_allowed"] = df["TD"].fillna(0) / att_safe

        df["net_yds_allowed_per_att"] = df["NY/A"]

        df["pressure_rate_def"] = df["Prss%"]

        yds_rank = df["pass_yds_allowed_per_att"].rank(ascending=True, method="average")
        td_rank  = df["pass_td_rate_allowed"].rank(ascending=True, method="average")
        prs_rank = df["pressure_rate_def"].rank(ascending=False, method="average")
        pts_rank = df["pts_allowed_per_game"].rank(ascending=True, method="average")

        composite = (
            0.4 * yds_rank +
            0.3 * td_rank +
            0.2 * prs_rank +
            0.1 * pts_rank
        )

        df["pass_defense_rank"] = composite.rank(ascending=True, method="dense")

        qb_def = df[[
            "Tm",
            "pts_allowed_per_game",
            "pass_yds_allowed_per_att",
            "pass_td_rate_allowed",
            "net_yds_allowed_per_att",
            "pressure_rate_def",
            "pass_defense_rank",
        ]].copy()

        return qb_def

    def calculate_rb_def_stats(self):
        return None