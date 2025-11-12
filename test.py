import nfl_data_py as nfl_dp
import nflreadpy as nfl_rp
from data_extractors.nfl_rp_extractor import NFLReadExtractor
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

extractor = NFLReadExtractor(2025)
raw_data = extractor.get_all_data()
df = raw_data['player_stats']

roster_weekly = extractor.load_snap_counts()
roster_weekly.to_csv('./data_extractors/data/snap_counts.csv', index=False)