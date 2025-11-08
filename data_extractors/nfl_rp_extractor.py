import nflreadpy as nfl_rp

class NFLReadExtractor:
    def __init__(self, player_stat_idxs, seasons):
        self.player_stat_idxs = player_stat_idxs
        self.seasons = seasons
        self.default_positions = ['QB', 'RB', 'WR', 'TE']
        
    
    def load_player_stats(self):
        if 'position' not in self.player_stat_idxs:
            self.player_stat_idxs.append('position')

        player_stats = nfl_rp.load_player_stats(self.seasons, 'reg').to_pandas()   
        player_stats = player_stats[self.player_stat_idxs]
        
        offensive_player_stats = player_stats[player_stats['position'].isin(self.default_positions)]

        return offensive_player_stats

    # also probably only need this current years stats to see how the 
    # offense and defense are doing to see if situation is good
    def load_team_stats(self):
        team_stats = nfl_rp.load_team_stats(self.seasons, 'reg').to_pandas()
        
        return team_stats


    # most likely only need current schedule for strength on schedule or honestly can scrape it from the web
    def load_schedules(self):
        return nfl_rp.load_schedules(self.seasons).to_pandas()
    

    # filter by players that dont have a last_season
    def load_players(self):
        return nfl_rp.load_players().to_pandas()
    

    # filter by positions we care about
    def load_rosters(self):
        return nfl_rp.load_rosters(self.seasons).to_pandas()
    

    # this is probably for finding the injury report and stuff and how depth chart is changing
    def load_rosters_weekly(self):
        return nfl_rp.load_rosters_weekly(self.seasons).to_pandas()
    

    def load_snap_counts(self):
        return nfl_rp.load_snap_counts(self.seasons).to_pandas()


    # default to always pass passing, rushing, recieving as a parameter seperately and combine all 3 into one
    # use player_gsis_id to combine the 3 different data frames
    # remember this receiving and rushing stats dont have for the other position so no wr in rushing and no rb in recieving 
    # next gen stats
    def load_nextgen_stats(self):
        return nfl_rp.load_nextgen_stats(self.seasons, 'receiving').to_pandas()
    

    # this probably isn't helpful because doesn't have current injuries
    def load_injuries(self):
        return nfl_rp.load_injuries([2024]).to_pandas()
    
    
    def load_ff_opportunity(self):
        # change 2025 to keep it at current season
        return nfl_rp.load_ff_opportunity(2025, 'weekly', 'latest')