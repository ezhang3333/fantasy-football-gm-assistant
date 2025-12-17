from services.espn_api import get_current_season
from constants import TEAM_NAME_TO_ABBR
import pandas as pd

class PFRDefCleaner:
    def __init__(self):
        self.year = get_current_season()
    
    def calculate_def_vs_rb(self, def_vs_rb):
        def_vs_rb = def_vs_rb.copy()

        def_vs_rb["def_rush_ypa_allowed"] = def_vs_rb["rush_yds"] / def_vs_rb["rush_att"]
        def_vs_rb["def_rb_carries_allowed"] = def_vs_rb["rush_att"] / def_vs_rb["games"]
        def_vs_rb["def_rb_receptions_allowed"] = def_vs_rb["rec_recept"] / def_vs_rb["games"]
        def_vs_rb["def_rb_touchdowns_allowed"] = (def_vs_rb["rush_tds"] + def_vs_rb["rec_tds"]) / def_vs_rb["games"]
        def_vs_rb["def_rb_fantasy_points_allowed"] = def_vs_rb["fantpt_per_game"]
        def_vs_rb["team_abbrev"] = def_vs_rb["team"].map(TEAM_NAME_TO_ABBR)

        rb_def = def_vs_rb[[
            "team_abbrev",
            "def_rush_ypa_allowed",
            "def_rb_carries_allowed",
            "def_rb_receptions_allowed",
            "def_rb_touchdowns_allowed",
            "def_rb_fantasy_points_allowed",            
        ]].copy()
        return rb_def
    
    def calculate_def_vs_te(self, def_vs_te):
        def_vs_te = def_vs_te.copy()

        def_vs_te["def_te_ftps"] = def_vs_te["fantpt_per_game"]
        def_vs_te["def_te_targets"] = def_vs_te["rec_tgts"] / def_vs_te["games"]
        def_vs_te["def_te_yards_per_target"] = def_vs_te["rec_yds"] / def_vs_te["rec_tgts"]
        def_vs_te["team_abbrev"] = def_vs_te["team"].map(TEAM_NAME_TO_ABBR)

        te_def = def_vs_te[[
            "team_abbrev",
            "def_te_ftps",
            "def_te_targets",
            "def_te_yards_per_target"
        ]].copy()
        return te_def
    
    def calculate_def_vs_qb(self, def_vs_qb):
        def_vs_qb = def_vs_qb.copy()

        def_vs_qb["def_pass_ypa_allowed"] = def_vs_qb["pass_yds"] / def_vs_qb["pass_att"]
        def_vs_qb["def_total_tds_allowed"] = (def_vs_qb["rush_tds"] + def_vs_qb["pass_tds"]) / def_vs_qb["games"]
        def_vs_qb["def_pass_int_rate_forced"] = def_vs_qb["pass_int"] / def_vs_qb["games"]
        def_vs_qb["def_sack_rate"] = def_vs_qb["sacks"] / def_vs_qb["games"]
        def_vs_qb["def_fantpt_allowed"] = def_vs_qb["fantpt_per_game"]
        def_vs_qb["def_rush_ypa_allowed"] = def_vs_qb["rush_yds"] / def_vs_qb["rush_att"]
        def_vs_qb["team_abbrev"] = def_vs_qb["team"].map(TEAM_NAME_TO_ABBR)

        qb_def = def_vs_qb[[
            "team_abbrev",
            "def_pass_ypa_allowed",
            "def_total_tds_allowed",
            "def_pass_int_rate_forced",
            "def_sack_rate",
            "def_fantpt_allowed",
            "def_rush_ypa_allowed"
        ]].copy()
        return qb_def
    
    def calculate_def_vs_wr(self, def_vs_wr):
        def_vs_wr = def_vs_wr.copy()

        def_vs_wr["def_wr_ftps"] = def_vs_wr["fantpt_per_game"]
        def_vs_wr["def_wr_targets"] = def_vs_wr["rec_tgts"] / def_vs_wr["games"]
        def_vs_wr["def_wr_yards_per_target"] = def_vs_wr["rec_yds"] / def_vs_wr["rec_tgts"]
        def_vs_wr["team_abbrev"] = def_vs_wr["team"].map(TEAM_NAME_TO_ABBR)

        wr_def = def_vs_wr[[
            "team_abbrev",
            "def_wr_ftps",
            "def_wr_targets",
            "def_wr_yards_per_target"
        ]].copy()
        return wr_def