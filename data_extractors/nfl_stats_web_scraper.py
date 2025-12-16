import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from data_cleaners.pfr_def_cleaner import PFRDefCleaner
from services.espn_api import get_current_season
import time

"""
team_def_stats : [
        'Rk', 'Tm', 'G', 'PA', 'Yds', 'Ply', 'Y/P', 'TO', 'FL', '1stD', 'Cmp',
       'Att', 'Yds', 'TD', 'Int', 'NY/A', '1stD', 'Att', 'Yds', 'TD', 'Y/A',
       '1stD', 'Pen', 'Yds', '1stPy', 'Sc%', 'TO%', 'EXP'
    ]

adv_def_stats : [
        'Tm', 'G', 'Att', 'Cmp', 'Yds', 'TD', 'DADOT', 'Air', 'YAC', 'Bltz',
       'Bltz%', 'Hrry', 'Hrry%', 'QBKD', 'QBKD%', 'Sk', 'Prss', 'Prss%',
       'MTkl'
    ]
"""
class NFLWebScraper:
    def __init__(self):
        self.year = get_current_season()

    def pfr_scrape_team_def_stats(self):
        pfr_team_def_url = f'https://www.pro-football-reference.com/years/{self.year}/opp.htm#all_team_stats'

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        driver.get(pfr_team_def_url)
        time.sleep(5)

        html = driver.page_source
        driver.quit()

        team_def_stats_uncleaned = self.extract_pfr_table(html, "all_team_stats")
        team_def_stats = self.pfr_clean_team_def_stats(team_def_stats_uncleaned)
        adv_def_stats = self.extract_pfr_table(html, "all_advanced_defense")

        return team_def_stats, adv_def_stats
    
    def pfr_scrape_def_vs_stats(self, year, position):
        capitalized_position = position.upper()
        pfr_team_def_url = f'https://www.pro-football-reference.com/years/{year}/fantasy-points-against-{capitalized_position}.htm'

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        driver.get(pfr_team_def_url)
        time.sleep(5)

        html = driver.page_source
        driver.quit()

        def_vs_stats_uncleaned = self.extract_pfr_table(html, "div_fantasy_def", "fantasy_def")
        def_vs_stats = self.pfr_clean_def_vs_stats(def_vs_stats_uncleaned)
        return def_vs_stats

    
    def cbs_scrape_team_def_stats(self, position):
        cbs_def_vs_stats_url = f"https://www.cbssports.com/fantasy/football/stats/posvsdef/{position}/ALL/avg/standard"
        renamed_columns = ['Rank', 'Team', 'Rush Att', 'Rush Yds', 'Rush YPA', 'Rush TD', 'Targt', 'Recpt', 'Rec Yds', 'YPC', 'Rec TD', 'FL', 'FPTS']

        response = requests.get(cbs_def_vs_stats_url, timeout=25)
        soup = BeautifulSoup(response.text, 'lxml')

        table = soup.select("table.data.compact")
        html_table = str(table)
        def_df = pd.read_html(html_table)[0]

        def_df = def_df.iloc[3:, :]
        def_df.columns = renamed_columns
        return def_df


    def extract_pfr_table(self, html, wrapper_id, table_id=None):
        soup = BeautifulSoup(html, "html.parser")
        
        wrapper = soup.find("div", id=wrapper_id)
        if wrapper is None:
            return None
        
        if table_id:
            table = wrapper.find("table", id=table_id)
        else:
            table = wrapper.find("table")

        if table is None:
            return None

        dfs = pd.read_html(str(table))
        return dfs[0]
    
    def pfr_clean_team_def_stats(self, team_def):
        team_def = team_def.copy()

        team_def.columns = team_def.columns.get_level_values(1)
        team_def = team_def[team_def["Rk"] != "Rk"]

        mask_mid_header = team_def["Rk"].isna() & team_def["Tm"].isna()
        team_def = team_def[~mask_mid_header]

        summary_labels = {"Avg Team", "League Total", "Avg Tm/G"}
        team_def = team_def[~team_def["Tm"].isin(summary_labels)]

        for i, col in enumerate(team_def.columns):
            if col == "Tm":
                continue
            team_def.iloc[:, i] = pd.to_numeric(team_def.iloc[:, i], errors="coerce")

        team_def = team_def.reset_index(drop=True)
        return team_def
    
    def pfr_clean_def_vs_stats(self, def_vs):
        def_vs = def_vs.copy()
        column_groups = {
            "Passing": ["completions", "pass_att", "pass_yds", "pass_tds", "pass_int", "2pp", "sacks"],
            "Rushing": ["rush_att", "rush_yds", "rush_tds"],
            "Receiving": ["rec_tgts", "rec_recept", "rec_yds", "rec_tds"],
            "Fantasy": ["fantpt", "dkpt", "fdpt"],
            "Fantasy per Game": ["fantpt_per_game", "dkpt_per_game", "fdpt_per_game"],
        }
        base_cols = ["team", "games"]

        stat_categories = def_vs.columns.get_level_values(0) 
        present_keys = set(stat_categories)

        group_order = ["Passing", "Rushing", "Receiving", "Fantasy", "Fantasy per Game"]

        grouped_cols = [column_groups[group] for group in group_order if group in present_keys]
        def_vs_cols = [col for group in grouped_cols for col in group]
        def_vs_cols = base_cols + def_vs_cols
        
        def_vs.columns = def_vs_cols
        return def_vs
