import streamlit as st
import pandas as pd
from scrape import load_fanduel_salaries
from projections import project_points
from optimizer import optimize_lineup
from lineups import scrape_lineups, match_names  # match_names is the fuzzy matcher

st.title("🚨 NHL FanDuel DFS Optimizer")

salary_file = st.file_uploader("Upload FanDuel CSV", type="csv")

if salary_file:
    df = load_fanduel_salaries(salary_file)

    # Add placeholder stats (replace with real stats later)
    df['Goals'] = 10
    df['Assists'] = 15
    df['Shots'] = 60
    df['BlockedShots'] = 20
    df['Projection'] = df.apply(project_points, axis=1)

    # Scrape DailyFaceoff line combinations
    lineup_df = scrape_lineups()

    # Fuzzy match FanDuel 'Nickname' to DailyFaceoff 'Player'
    name_map = match_names(df['Nickname'], lineup_df['Player'])

    # Map FanDuel nicknames to matched DailyFaceoff full names
    df['MatchedName'] = df['Nickname'].map(name_map)

    # Add power play and even strength flags using matched names
    df['on_PP1'] = df['MatchedName'].isin(
        lineup_df[(lineup_df.LineType == 'PP') & (lineup_df.LineNumber == '1')]['Player']
    )
    df['on_EV1'] = df['MatchedName'].isin(
        lineup_df[(lineup_df.LineType == 'EV') & (lineup_df.LineNumber == '1')]['Player']
    )

    # Show the lineup combos scraped
    st.subheader("🧩 Line Combinations (DailyFaceoff)")
    st.dataframe(lineup_df)

    # Show the fuzzy name matches (debugging aid)
    st.subheader("🔎 Name Matching (FanDuel ➜ DailyFaceoff)")
    st.dataframe(pd.DataFrame(name_map.items(), columns=["FanDuel Nickname", "Matched Name"]))

    # Show player projections
    st.subheader("📊 Player Projections")
    st.dataframe(df.sort_values("Projection", ascending=False))

    # Optimize and show the lineup
    st.subheader("🧮 Optimized Lineup")
    lineup = optimize_lineup(df)
    st.dataframe(lineup[['Nickname', 'Position', 'Salary', 'Projection']])
