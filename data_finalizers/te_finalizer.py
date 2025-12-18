from constants import te_calculated_stats
from services.espn_api import get_current_week

class TEFinalizer:
    def __init__(self, te_cleaned_dataset):
        self.te_cleaned_dataset = te_cleaned_dataset
        self.current_week = get_current_week()

    def extract_finalized_dataset(self):
        identifiers = ["team", "position", "full_name", "gsis_id", "week", "season"]
        cleaned = self.te_cleaned_dataset
        curr_week = self.current_week
        all_columns_to_extract = identifiers + te_calculated_stats
        
        if self.current_week == 1:
            return cleaned[all_columns_to_extract]
        else:
            te_cleaned_correct_weeks = cleaned[cleaned["week"].between(1, curr_week - 1)]
            return te_cleaned_correct_weeks[all_columns_to_extract]