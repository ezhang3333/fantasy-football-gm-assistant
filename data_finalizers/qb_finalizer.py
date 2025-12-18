import pandas as pd
from constants import qb_calculated_stats
from services.espn_api import get_current_week

class QBFinalizer:
    def __init__(self, qb_cleaned_dataset):
        self.qb_cleaned_dataset = qb_cleaned_dataset
        self.current_week = get_current_week()

    def extract_finalized_dataset(self):
        identifiers = ["team", "position", "full_name", "gsis_id", "week", "season"]
        cleaned = self.qb_cleaned_dataset
        curr_week = self.current_week
        all_columns_to_extract = identifiers + qb_calculated_stats
        
        if self.current_week == 1:
            return cleaned[all_columns_to_extract]
        else:
            qb_cleaned_correct_weeks = cleaned[cleaned["week"].between(1, curr_week - 1)]
            return qb_cleaned_correct_weeks[all_columns_to_extract]