import nfl_data_py as nfl_dp
import nflreadpy as nfl_rp
from data_extractors.nfl_rp_extractor import NFLReadExtractor

player_stat_idxs = ['player_name', 'player_display_name', 'position', 'fantasy_points', 'fantasy_points_ppr']
extractor = NFLReadExtractor(player_stat_idxs, [2025])

player_stats = extractor.load_player_stats()
#print(player_stats)

team_stats = extractor.load_team_stats()
print(team_stats.columns.tolist())