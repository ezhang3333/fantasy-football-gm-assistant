from data_extractors.nfl_rp_extractor import NFLReadExtractor
from data_extractors.nfl_stats_web_scraper import NFLWebScraper
from data_cleaners.pfr_def_cleaner import PFRDefCleaner

web_scraper = NFLWebScraper()
def_vs_rb = web_scraper.pfr_scrape_def_vs_stats("2025", "RB")
def_vs_te = web_scraper.pfr_scrape_def_vs_stats("2025", "TE")
def_vs_qb = web_scraper.pfr_scrape_def_vs_stats("2025", "QB")
def_vs_wr = web_scraper.pfr_scrape_def_vs_stats("2025", "WR")

pfr_def_cleaner = PFRDefCleaner()
cleaned_def_vs_rb = pfr_def_cleaner.calculate_def_vs_rb(def_vs_rb)
cleaned_def_vs_te = pfr_def_cleaner.calculate_def_vs_te(def_vs_te)
cleaned_def_vs_qb = pfr_def_cleaner.calculate_def_vs_qb(def_vs_qb)
cleaned_def_vs_wr = pfr_def_cleaner.calculate_def_vs_wr(def_vs_wr)

print(cleaned_def_vs_rb)
print(cleaned_def_vs_te)
print(cleaned_def_vs_qb)
print(cleaned_def_vs_wr)
