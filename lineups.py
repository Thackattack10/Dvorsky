import requests
import pandas as pd
from bs4 import BeautifulSoup
from rapidfuzz import process

def scrape_lineups():
    url = "https://dailyfaceoff.com/teams/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    teams = []
    players = []
    line_types = []
    line_numbers = []

    for team_section in soup.select(".team-roster"):
        # Team name, e.g. 'Toronto Maple Leafs'
        team_name = team_section.find("h3").text.strip()

        # For each line type (EV, PP, PK, etc.)
        for line_group in team_section.select(".lines-group"):
            line_type = line_group.find("h4").text.strip()

            for idx, player_li in enumerate(line_group.select("ul > li"), start=1):
                player_name = player_li.text.strip()
                teams.append(team_name)
                players.append(player_name)
                line_types.append(line_type)
                line_numbers.append(str(idx))

    df = pd.DataFrame({
        "Team": teams,
        "Player": players,
        "LineType": line_types,
        "LineNumber": line_numbers,
    })

    return df

def match_names(fanduel_names, dailyfaceoff_names, score_cutoff=80):
    name_map = {}
    for short_name in fanduel_names:
        match, score, _ = process.extractOne(short_name, dailyfaceoff_names, score_cutoff=score_cutoff)
        if match:
            name_map[short_name] = match
        else:
            # No good match found; map to None or original name
            name_map[short_name] = None
    return name_map
