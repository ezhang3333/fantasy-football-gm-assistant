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

class NFLDataPipeline:
    def __init__(self, years_of_data):
        self.years_of_data = years_of_data

    def extract_raw_data():
        return None
    
    def clean_raw_data():
        return None
    