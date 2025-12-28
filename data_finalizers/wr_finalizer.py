from constants import wr_calculated_stats
from services.espn_api import get_current_week, get_current_season

class WRFinalizer:
    def __init__(self, wr_cleaned_dataset):
        self.wr_cleaned_dataset = wr_cleaned_dataset
        self.current_week = get_current_week()
        self.current_season = get_current_season()

    def extract_finalized_dataset(self):
        identifiers = ["team", "position", "full_name", "gsis_id", "week", "season"]
        cleaned = self.wr_cleaned_dataset
        curr_week = self.current_week
        curr_season = self.current_season
        all_columns_to_extract = identifiers + wr_calculated_stats
        
        if curr_week <= 1:
            final = cleaned[all_columns_to_extract].copy()
            final = final.dropna(subset=all_columns_to_extract)
            return final

        mask_prior_seasons = cleaned["season"] < curr_season
        mask_current_season = (cleaned["season"] == curr_season) & cleaned["week"].between(1, curr_week - 1)

        final = cleaned[mask_prior_seasons | mask_current_season]
        final = final[all_columns_to_extract].copy()
        final = final.dropna(subset=all_columns_to_extract)

        return final