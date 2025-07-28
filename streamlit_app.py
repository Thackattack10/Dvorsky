import streamlit as st
import pandas as pd
from scrape import load_fanduel_salaries
from projections import project_points
from optimizer import optimize_lineup
from lineups import scrape_lineups

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

    # 🧩 Scrape and match line combos
    lineup_df = scrape_lineups()
    df['on_PP1'] = df['Nickname'].isin(
        lineup_df[(lineup_df.LineType == 'PP') & (lineup_df.LineNumber == '1')]['Player']
    )
    df['on_EV1'] = df['Nickname'].isin(
        lineup_df[(lineup_df.LineType == 'EV') & (lineup_df.LineNumber == '1')]['Player']
    )

    st.subheader("🧩 Line Combinations (DailyFaceoff)")
    st.dataframe(lineup_df)

    st.subheader("📊 Player Projections")
    st.dataframe(df.sort_values("Projection", ascending=False))

    st.subheader("🧮 Optimized Lineup")
    lineup = optimize_lineup(df)
    st.dataframe(lineup[['Nickname', 'Position', 'Salary', 'Projection']])
