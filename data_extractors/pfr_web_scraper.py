import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
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

        print(f"[INFO] Loading page {pfr_team_def_url} ...")
        driver.get(pfr_team_def_url)

        time.sleep(5)

        html = driver.page_source
        driver.quit()

        print("[INFO] Parsing tables...")
        dfs = pd.read_html(html)

        print(f"[INFO] Found {len(dfs)} tables")
        return dfs
    
hi = PFRWebScraper()
hi.scrape_team_def_stats()