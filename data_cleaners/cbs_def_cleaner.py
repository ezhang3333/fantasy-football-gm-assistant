import pandas as pd
from constants import TEAM_NAME_TO_ABBR

TEAM_NICK_TO_ABBR = {
    full_name.split()[-1]: abbr
    for full_name, abbr in TEAM_NAME_TO_ABBR.items()
}

class CBSDefCleaner:
    def __init__(self, cbs_def_vs_rb_stats):
        self.cbs_def_vs_rb_stats = cbs_def_vs_rb_stats.copy()
        self.calculated_stats = {
            'cbs_def_vs_rb_stats' : [
                "def_rush_ypa_allowed", 
                "def_rb_carries_allowed", 
                "def_rb_receptions_allowed", 
                "def_rb_touchdowns_allowed", 
                "def_rb_fantasy_points_allowed"
            ]
        }

    def calculate_cbs_def_vs_rb_stats(self):
        rb_def_df = self.cbs_def_vs_rb_stats.copy()

        rb_def_df["def_rush_ypa_allowed"] = rb_def_df["Rush YPA"]
        rb_def_df["def_rb_carries_allowed"] = rb_def_df["Rush Att"]
        rb_def_df["def_rb_receptions_allowed"] = rb_def_df["Recpt"]
        rb_def_df["def_rb_touchdowns_allowed"] = (rb_def_df["Rush TD"] + rb_def_df["Rec TD"])
        rb_def_df["def_rb_fantasy_points_allowed"] = rb_def_df["FPTS"]

        rb_def_df["TeamNickname"] = (
            rb_def_df["Team"]
            .str.replace("RB vs ", "", regex=False)
            .str.strip()
        )
        rb_def_df["team"] = rb_def_df["TeamNickname"].map(TEAM_NICK_TO_ABBR)

        rb_def_df = rb_def_df.dropna(subset=["team"])

        result_df = rb_def_df[[
            "team",
            "def_rush_ypa_allowed",
            "def_rb_carries_allowed",
            "def_rb_receptions_allowed",
            "def_rb_touchdowns_allowed",
            "def_rb_fantasy_points_allowed",
        ]].reset_index(drop=True)

        return result_df

