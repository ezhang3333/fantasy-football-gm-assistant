from data_extractors.nfl_rp_extractor import NFLReadExtractor
from data_extractors.nfl_stats_web_scraper import NFLWebScraper
from data_cleaners.pfr_def_cleaner import PFRDefCleaner

web_scraper = NFLWebScraper()
def_vs = web_scraper.pfr_scrape_def_vs_stats("2025", "RB")

pfr_def_cleaner = PFRDefCleaner()
cleaned_def_vs = pfr_def_cleaner.calculate_def_vs_rb(def_vs)
print(cleaned_def_vs)

