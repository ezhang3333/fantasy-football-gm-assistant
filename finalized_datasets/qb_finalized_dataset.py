# not sure if you need this import
from data_cleaners.positions.qb_cleaner import QBCleaner
import time

class QBFinalizedDataset:
    def __init__(self, qb_cleaned_dataset):
        self.qb_cleaned_dataset = qb_cleaned_dataset
        self.current_week = 0
    
    def determine_current_week(self):
        # figure out consistent way to determine the current week of the nfl