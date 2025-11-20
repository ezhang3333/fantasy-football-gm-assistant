import nfl_data_py as nfl_dp
import nflreadpy as nfl_rp
from data_extractors.nfl_rp_extractor import NFLReadExtractor
from data_cleaners.nfl_rp_cleaner import NFLReadCleaner
from data_cleaners.pfr_def_cleaner import PFRDefCleaner
from data_extractors.pfr_web_scraper import PFRWebScraper
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


extractor = NFLReadExtractor(2025)


# if you need to reupdate the data in data extractors
# roster_weekly = extractor.load_snap_counts()
# roster_weekly.to_csv('./data_extractors/data/snap_counts.csv', index=False)


# # for testing the cleaner
# cleaner = NFLReadCleaner(raw_data)
# merged = cleaner.merge_data_to_player_weeks()
# #print(merged.columns)
# merged.to_csv('./data_cleaners/data/data.csv', index=False)

hi = PFRWebScraper()
tuple = hi.scrape_team_def_stats()
team_def_stats = tuple[0]
adv_def_stats = tuple[1]
# tuple[0].to_csv('data/team_def_stats.csv', index=False)
# tuple[1].to_csv('data/adv_def_stats.csv', index=False)
# print(team_def_stats.columns)
# print(adv_def_stats.columns)
DefCleaner = PFRDefCleaner(team_def_stats=team_def_stats, adv_def_stats=adv_def_stats)
def_ranking = DefCleaner.calculate_qb_def_stats()
print(def_ranking)
