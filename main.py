import requests

espn_url = 'https://partners.api.espn.com/v2/sports/football/nfl/athletes?limit=7000'
second_espn_url = 'https://sports.core.api.espn.com/v3/sports/football/nfl/athletes?page=1&limit=20000'
response = requests.get(espn_url)
second_response = requests.get(second_espn_url)

print(second_response.json())
#print(response.status_code)
#print(response.json())

# going to have to do web scraping

