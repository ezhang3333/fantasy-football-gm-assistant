from data_extractors.nfl_rp_extractor import NFLReadExtractor
from data_cleaners.nfl_rp_cleaner import NFLReadCleaner
from data_extractors.nfl_stats_web_scraper import NFLWebScraper
from data_cleaners.pfr_def_cleaner import PFRDefCleaner
from data_cleaners.positions.qb_cleaner import QBCleaner
from data_finalizers.qb_finalizer import QBFinalizer
from data_cleaners.cbs_def_cleaner import CBSDefCleaner
from data_cleaners.positions.rb_cleaner import RBCleaner
from data_finalizers.rb_finalizer import RBFinalizer
from data_cleaners.positions.wr_cleaner import WRCleaner
from data_finalizers.wr_finalizer import WRFinalizer
from data_cleaners.positions.te_cleaner import TECleaner
from data_finalizers.te_finalizer import TEFinalizer
import pandas as pd

class NFLDataPipeline:
    def __init__(self, seasons):
        self.seasons = seasons

        self.extractor = NFLReadExtractor(self.seasons)
        self.scraper = NFLWebScraper()

        self.qb_cleaner = QBCleaner()
        self.rb_cleaner = RBCleaner()
        self.wr_cleaner = WRCleaner()
        self.te_cleaner = TECleaner()
        self.pfr_cleaner = PFRDefCleaner()

        self.qb_finalizer = QBFinalizer()
        self.rb_finalizer = RBFinalizer()
        self.wr_finalizer = WRFinalizer()
        self.te_finalizer = TEFinalizer()


    def extract_raw_data(self):
        return self.extractor.get_all_data()
    
    def clean_raw_data(self):
        def_vs_qb = self.scraper.pfr_clean_def_vs_stats()
    
    def finalize_datasets(self):
        return None