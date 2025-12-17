from data_extractors.nfl_rp_extractor import NFLReadExtractor
from data_cleaners.nfl_rp_cleaner import NFLReadCleaner
from data_cleaners.pfr_def_cleaner import PFRDefCleaner
from data_extractors.nfl_stats_web_scraper import NFLWebScraper
import pandas as pd
from data_cleaners.positions.qb_cleaner import QBCleaner
from data_finalizers.qb_finalizer import QBFinalizer
from data_cleaners.cbs_def_cleaner import CBSDefCleaner
from data_cleaners.positions.rb_cleaner import RBCleaner
from data_finalizers.rb_finalizer import RBFinalizer
from data_cleaners.positions.wr_cleaner import WRCleaner
from data_finalizers.wr_finalizer import WRFinalizer
from data_cleaners.positions.te_cleaner import TECleaner
from data_finalizers.te_finalizer import TEFinalizer

extractor = NFLReadExtractor()
raw_data = extractor.get_all_data()

cleaner = NFLReadCleaner(raw_data)
merged = cleaner.merge_data_to_player_weeks()
# merged.to_csv('./data_cleaners/data/merged_data.csv', index=False)

hi = NFLWebScraper()
tuple = hi.pfr_scrape_team_def_stats()
cbs_def_wr_stats = hi.cbs_scrape_team_def_stats("WR")
cbs_def_rb_stats = hi.cbs_scrape_team_def_stats("RB")
cbs_def_te_stats = hi.cbs_scrape_team_def_stats("TE")

cbs = CBSDefCleaner(cbs_def_rb_stats, cbs_def_wr_stats, cbs_def_te_stats)
cbs_def_vs_rb_final = cbs.calculate_cbs_def_vs_rb_stats()
cbs_def_vs_wr_final = cbs.calculate_cbs_def_vs_wr_stats()
cbs_def_vs_te_final = cbs.calculate_cbs_def_vs_te_stats()
# df.to_csv('data_extractors/data/cbs_team_def.csv', index=False)
team_def_stats = tuple[0]
adv_def_stats = tuple[1]

DefCleaner = PFRDefCleaner(team_def_stats=team_def_stats, adv_def_stats=adv_def_stats)
qb_def_stats = DefCleaner.calculate_qb_def_stats()

qb = QBCleaner(merged, qb_def_stats)
qb_cleaned_dataset = qb.add_calculated_stats()
# qb_cleaned_dataset.to_csv('data_cleaners/data/qb_data.csv', index=False)

qb_finalized = QBFinalizer(qb_cleaned_dataset)
qb_finalized_dataset = qb_finalized.extract_finalized_dataset()
# qb_finalized_dataset.to_csv('./finalized_datasets/data/qb_finalized_dataset.csv', index=False)

rb = RBCleaner(merged, cbs_def_vs_rb_final)
rb_cleaned = rb.add_calculated_stats()
# rb_cleaned.to_csv('./data_cleaners/data/rb_data.csv', index=False)

rb_finalized = RBFinalizer(rb_cleaned)
rb_finalized_dataset = rb_finalized.extract_finalized_dataset()
# rb_finalized_dataset.to_csv('./finalized_datasets/data/rb_finalized_dataset.csv', index=False)

wr = WRCleaner(merged, cbs_def_vs_wr_final)
wr_cleaned = wr.add_calculated_stats()
# wr_cleaned.to_csv('./data_cleaners/data/wr_data.csv', index=False)

wr_finalized = WRFinalizer(wr_cleaned)
wr_finalized_dataset = wr_finalized.extract_finalized_dataset()
# wr_finalized_dataset.to_csv('./finalized_datasets/data/wr_finalized_dataset.csv', index=False)

te = TECleaner(merged, cbs_def_vs_te_final)
te_cleaned = te.add_calculated_stats()
te_cleaned.to_csv('./data_cleaners/data/te_data.csv', index=False)

te_finalized = TEFinalizer(te_cleaned)
te_finalized_dataset = te_finalized.extract_finalized_dataset()
te_finalized_dataset.to_csv('./finalized_datasets/data/te_finalized_dataset.csv', index=False)
