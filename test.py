import nfl_data_py as nfl_dp
import nflreadpy as nfl_rp
from data_extractors.nfl_rp_extractor import NFLReadExtractor
from data_cleaners.nfl_rp_cleaner import NFLReadCleaner
from data_cleaners.pfr_def_cleaner import PFRDefCleaner
from data_extractors.nfl_stats_web_scraper import NFLWebScraper
import pandas as pd
from data_cleaners.positions.qb_cleaner import QBCleaner
from finalized_datasets.qb_finalized_dataset import QBFinalizedDataset
from data_cleaners.cbs_def_cleaner import CBSDefCleaner
from data_cleaners.positions.rb_cleaner import RBCleaner

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


extractor = NFLReadExtractor(2025)
raw_data = extractor.get_all_data()

# if you need to reupdate the data in data extractors
# roster_weekly = extractor.load_snap_counts()
# roster_weekly.to_csv('./data_extractors/data/snap_counts.csv', index=False)


# # for testing the cleaner
cleaner = NFLReadCleaner(raw_data)
merged = cleaner.merge_data_to_player_weeks()
# merged.to_csv('./data_cleaners/data/merged_data.csv', index=False)

hi = NFLWebScraper()
# tuple = hi.pfr_scrape_team_def_stats()
cbs_def_stats = hi.cbs_scrape_team_def_stats()

cbs = CBSDefCleaner(cbs_def_stats)
cbs_def_vs_rb_final = cbs.calculate_cbs_def_vs_rb_stats()
print(cbs_def_vs_rb_final)
# df.to_csv('data_extractors/data/cbs_team_def.csv', index=False)
# team_def_stats = tuple[0]
# adv_def_stats = tuple[1]
# tuple[0].to_csv('data/team_def_stats.csv', index=False)
# tuple[1].to_csv('data/adv_def_stats.csv', index=False)
# print(team_def_stats.columns)
# print(adv_def_stats.columns)
# DefCleaner = PFRDefCleaner(team_def_stats=team_def_stats, adv_def_stats=adv_def_stats)
# qb_def_stats = DefCleaner.calculate_qb_def_stats()

# qb = QBCleaner(merged, qb_def_stats)
# qb_cleaned_dataset = qb.add_calculated_stats()
# qb_calculated_stats.to_csv('data_cleaners/data/qb_data.csv', index=False)

# qb_finalized = QBFinalizedDataset(qb_cleaned_dataset)
# qb_finalized_dataset = qb_finalized.extract_finalized_dataset()
# qb_finalized_dataset.to_csv('./finalized_datasets/data/qb_finalized_dataset.csv', index=False)

rb = RBCleaner(merged, cbs_def_vs_rb_final)
rb.add_calculated_stats()