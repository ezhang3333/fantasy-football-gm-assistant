import nfl_data_py as nfl_dp
import nflreadpy as nfl_rp
from data_extractors.nfl_rp_extractor import NFLReadExtractor
from data_cleaners.nfl_rp_cleaner import NFLReadCleaner
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


extractor = NFLReadExtractor(2025)
extractor.calculate_def_rankings()


# if you need to reupdate the data in data extractors
# roster_weekly = extractor.load_snap_counts()
# roster_weekly.to_csv('./data_extractors/data/snap_counts.csv', index=False)


# # for testing the cleaner
# cleaner = NFLReadCleaner(raw_data)
# merged = cleaner.merge_data_to_player_weeks()
# #print(merged.columns)
# merged.to_csv('./data_cleaners/data/data.csv', index=False)
