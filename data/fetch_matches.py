from datetime import date, timedelta
from urllib import response
import requests
import json
from dotenv import load_dotenv
import os

DELTA_TIME = timedelta(days=7) #fetch_matches gets all matches in the next weeks
API_ROOT = 'http://api.football-data.org'

def run():
    start = date.today().strftime("%Y-%m-%d")
    end = (date.today() + DELTA_TIME).strftime("%Y-%m-%d")

    url = f'{API_ROOT}/v4/competitions/WC/matches?dateFrom={start}&dateTo={end}'
    
    load_dotenv()
    header = {'X-Auth-Token': os.getenv("MATCHES_API_KEY")}
    
    response = requests.get(url, headers=header)
    matches = []

    for v in response.json()['matches']:
        match_data = {
            "id": v["id"],
            "team1": v["homeTeam"]["name"],
            "team2": v["awayTeam"]["name"],
            "date": v["utcDate"][:10],
            "time": v["utcDate"][11:16]
        }
        #the api includes matches whos players haven't been decided yet, so excluding them before adding to matches
        if None not in match_data.values():
            matches.append(match_data)

    with open("data/matches.json", "w") as file:
        json.dump(matches, file, indent=4)
