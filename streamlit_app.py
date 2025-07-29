from lineups import scrape_lineups, match_names
import streamlit as st
import pandas as pd
from scrape import load_fanduel_salaries
from projections import project_points
from optimizer import optimize_lineup

# --- 🔥 Custom background + neon title style ---
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
                    url("https://www.pittsburghmagazine.com/content/uploads/data-import/78da5ad9/slapshotlarge.jpeg");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
    }}

    .stDataFrame, .stTable {{
        background-color: rgba(0, 0, 0, 0.6);
        color: white;
    }}

    .neon-title {{
        font-family: 'Arial Black', sans-serif;
        font-size: 3rem;
        color: #fff;
        text-align: center;
        text-shadow:
            0 0 5px #00FFFF,
            0 0 10px #00FFFF,
            0 0 20px #00FFFF,
            0 0 40px #00FFFF,
            0 0 80px #00FFFF;
        animation: flicker 3s infinite alternate;
    }}

    @keyframes flicker {{
        0%   {{ opacity: 1; }}
        45%  {{ opacity: 0.85; }}
        60%  {{ opacity: 1; }}
        75%  {{ opacity: 0.9; }}
        100% {{ opacity: 1; }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 🚨 Title ---
st.markdown('<h1 class="neon-title">🚨 Mikey\'s Daily Lineups</h1>', unsafe_allow_html=True)

# --- Upload CSV ---
salary_file = st.file_uploader("Upload FanDuel CSV", type="csv")

if salary_file:
    try:
        df = load_fanduel_salaries(salary_file)
    except Exception as e:
        st.error(f"Error loading FanDuel salaries file: {e}")
        st.stop()

    required_columns = ['Nickname', 'Salary', 'Position']
    if not all(col in df.columns for col in required_columns):
        st.error(f"Missing required columns: {', '.join(required_columns)}")
        st.stop()

    # Placeholder stats
    df['Goals'] = 12
    df['Assists'] = 8
    df['Shots'] = 1.6
    df['BlockedShots'] = 1.6

    # Calculate projection per player
    df['Projection'] = df.apply(project_points, axis=1)
    df['Projection'].fillna(0, inplace=True)

    # Scrape lineup data
    lineup_df = scrape_lineups()

    # Fuzzy match FanDuel nicknames to DailyFaceoff players
    name_map = match_names(df['Nickname'], lineup_df['Player'])

    # Map nicknames to matched names
    df['MatchedName'] = df['Nickname'].map(name_map)

    # Flags for power play and even strength 1st lines
    df['on_PP1'] = df['MatchedName'].isin(
        lineup_df[(lineup_df.LineType == 'PP') & (lineup_df.LineNumber == '1')]['Player']
    )
    df['on_EV1'] = df['MatchedName'].isin(
        lineup_df[(lineup_df.LineType == 'EV') & (lineup_df.LineNumber == '1')]['Player']
    )

    # Display scraped line combinations
    st.subheader("🧩 Line Combinations (DailyFaceoff)")
    st.dataframe(lineup_df)

    # Show fuzzy matching results for debugging
    st.subheader("🔎 Name Matching (FanDuel ➜ DailyFaceoff)")
    st.dataframe(pd.DataFrame(name_map.items(), columns=["FanDuel Nickname", "Matched Name"]))

    # Show player projections sorted descending
    st.subheader("📊 Player Projections")
    st.dataframe(df.sort_values("Projection", ascending=False))

    # Optimize lineup
    st.subheader("🧮 Optimized Lineup")
    lineup = optimize_lineup(df)

    # Show optimized lineup with key info
    st.dataframe(lineup[['Nickname', 'Position', 'Salary', 'Projection']])

    # Show summary info: total salary and total projected points
    total_salary = lineup['Salary'].sum()
    total_projection = lineup['Projection'].sum()
    st.write(f"**Total Salary:** ${total_salary}")
    st.write(f"**Total Projected Points:** {total_projection:.2f}")

else:
    st.info("Please upload a FanDuel CSV file to get started.")
