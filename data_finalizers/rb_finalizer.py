from constants import rb_calculated_stats
from services.espn_api import get_current_week

class RBFinalizer:
    def __init__(self, rb_cleaned_dataset):
        self.rb_cleaned_dataset = rb_cleaned_dataset
        self.current_week = get_current_week()

    def extract_finalized_dataset(self):
        identifiers = ["team", "position", "full_name", "gsis_id", "week"]
        cleaned = self.rb_cleaned_dataset
        curr_week = self.current_week
        all_columns_to_extract = identifiers + rb_calculated_stats
        
        if self.current_week == 1:
            return cleaned[all_columns_to_extract]
        else:
            rb_cleaned_correct_weeks = cleaned[cleaned["week"].between(1, curr_week - 1)]
            return rb_cleaned_correct_weeks[all_columns_to_extract]