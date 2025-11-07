import nflreadpy as nfl_rp

class NFLReadExtractor:
    def __init__(self, player_stats, seasons):
        self.player_stats = player_stats
        self.seasons = seasons
        self.default_positions = ['QB', 'RB', 'WR', 'TE']

    
    def load_player_stats(self):
        if 'position' not in self.player_stats:
            self.player_stats.append('position')
            
        player_stats = nfl_rp.load_player_stats(self.seasons, 'reg').to_pandas()   
        player_stats = player_stats[self.player_stats]
        
        offensive_player_stats = player_stats[player_stats['position'].isin(self.default_positions)]

        return offensive_player_stats

    def load_team_stats(self):
        team_stats = nfl_rp.load_team_stats(self.seasons, 'reg').to_pandas()
        
        return team_stats

    def load_schedules(self):
        return nfl_rp.load_schedules(self.seasons).to_pandas()
    
    def load_players(self):
        return nfl_rp.load_players().to_pandas()
    
    def load_rosters(self):
        return nfl_rp.load_rosters(self.seasons).to_pandas()
    
    def load_rosters_weekly(self):
        return nfl_rp.load_rosters_weekly(self.seasons).to_pandas()
    
    def load_snap_counts(self):
        return nfl_rp.load_snap_counts(self.seasons).to_pandas()

    def load_nextgen_stats(self):
        return nfl_rp.load_nextgen_stats(self.seasons).to_pandas()
    
    def load_injuries(self):
        return nfl_rp.load_nextgen_stats()