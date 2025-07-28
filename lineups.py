import requests
from bs4 import BeautifulSoup
import pandas as pd

TEAM_SLUGS = [
    "boston-bruins", "chicago-blackhawks", "detroit-red-wings",
    "edmonton-oilers", "montreal-canadiens", "toronto-maple-leafs",
    # … include all 32 NHL teams with their dailyfaceoff slugs
]

def scrape_lineups():
    rows = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for slug in TEAM_SLUGS:
        url = f"https://www.dailyfaceoff.com/teams/{slug}/line-combinations/"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"Warning: Could not fetch {slug}")
            continue
        soup = BeautifulSoup(res.text, "html.parser")
        team = slug.replace("-", " ").title()

        for section in soup.find_all("h3"):
            section_name = section.get_text(strip=True)
            if "Even" in section_name or "Power" in section_name:
                table = section.find_next("table")
                if not table:
                    continue
                lt = "EV" if "Even" in section_name else "PP"
                for tr in table.find_all("tr")[1:]:
                    cols = [td.get_text(strip=True) for td in tr.find_all("td")]
                    if not cols or len(cols) < 2:
                        continue
                    line_num = cols[0]
                    players = [p.strip() for p in cols[1].split(",")]
                    for p in players:
                        rows.append({
                            "Team": team,
                            "LineType": lt,
                            "LineNumber": line_num,
                            "Player": p
                        })

    return pd.DataFrame(rows)
