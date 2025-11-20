import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

class PFRWebScraper:
    def __init__(self):
        # TODO: create get current season function
        self.year = 2025

    def scrape_team_def_stats(self):
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
        team_def_stats = self.clean_team_def_stats(team_def_stats_uncleaned)
        adv_def = self.extract_pfr_table(html, "all_advanced_defense")

        return team_def_stats, adv_def
    
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
    
    def clean_team_def_stats(self, df_raw):
        df = df_raw.copy()

        df.columns = df.columns.get_level_values(1)
        df = df[df["Rk"] != "Rk"]

        mask_mid_header = df["Rk"].isna() & df["Tm"].isna()
        df = df[~mask_mid_header]

        summary_labels = {"Avg Team", "League Total", "Avg Tm/G"}
        df = df[~df["Tm"].isin(summary_labels)]

        for i, col in enumerate(df.columns):
            if col == "Tm":
                continue
            df.iloc[:, i] = pd.to_numeric(df.iloc[:, i], errors="coerce")

        df = df.reset_index(drop=True)
        return df

    
""" Testing Web Scraper
hi = PFRWebScraper()
tuple = hi.scrape_team_def_stats()
tuple[0].to_csv('data/team_def_stats.csv', index=False)
tuple[1].to_csv('data/adv_def_stats.csv', index=False)
"""