from lineups import scrape_lineups, match_names
import streamlit as st
import pandas as pd
from scrape import load_fanduel_salaries
from projections import project_points
from optimizer import optimize_lineup

# --- 🎨 Retro Style + Background ---
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)),
                    url("https://www.pittsburghmagazine.com/content/uploads/data-import/78da5ad9/slapshotlarge.jpeg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        font-family: 'Press Start 2P', monospace;
        color: #00ffff;
    }}

    h1.neon-title {{
        font-size: 2.5rem;
        text-align: center;
        color: #ff00cc;
        text-shadow:
            0 0 5px #ff00cc,
            0 0 10px #ff00cc,
            0 0 20px #ff00cc,
            0 0 40px #ff00cc,
            0 0 80px #ff00cc;
        animation: flicker 1.8s infinite alternate;
        margin-bottom: 2rem;
    }}

    .stButton button {{
        background-color: #00ffff;
        color: black;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 20px;
        border: 2px solid #ff00cc;
        box-shadow: 0 0 10px #00ffff;
    }}

    .stDataFrame, .stTable {{
        background-color: rgba(0, 0, 0, 0.85);
        color: #00ffff;
        font-size: 10px;
    }}

    @keyframes flicker {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
        100% {{ opacity: 1; }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 🚨 Neon Title ---
st.markdown('<h1 class="neon-title">🚨 Mikey\'s Algorithm Bitch 🚨</h1>', unsafe_allow_html=True)

# --- 📂 Upload CSV ---
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

    # --- 📊 Placeholder Stats ---
    df['Goals'] = 12
    df['Assists'] = 8
    df['Shots'] = 1.6
    df['BlockedShots'] = 1.6

    df['Projection'] = df.apply(project_points, axis=1)
    df['Projection'].fillna(0, inplace=True)

    # --- 🧩 Scrape Line Combinations ---
    lineup_df = scrape_lineups()

    name_map = match_names(df['Nickname'], lineup_df['Player'])
    df['MatchedName'] = df['Nickname'].map(name_map)

    df['on_PP1'] = df['MatchedName'].isin(
        lineup_df[(lineup_df.LineType == 'PP') & (lineup_df.LineNumber == '1')]['Player']
    )
    df['on_EV1'] = df['MatchedName'].isin(
        lineup_df[(lineup_df.LineType == 'EV') & (lineup_df.LineNumber == '1')]['Player']
    )

    # --- 🧩 Show Line Combinations ---
    st.subheader("🧩 Line Combinations (DailyFaceoff)")
    st.dataframe(lineup_df)

    # --- 🔍 Name Matching ---
    st.subheader("🔎 Name Matching (FanDuel ➜ DailyFaceoff)")
    st.dataframe(pd.DataFrame(name_map.items(), columns=["FanDuel Nickname", "Matched Name"]))

    # --- 📊 Player Projections ---
    st.subheader("📊 Player Projections")
    st.dataframe(df.sort_values("Projection", ascending=False))

    # --- 🧮 Optimized Lineup ---
    st.subheader("🧮 Optimized Lineup")
    lineup = optimize_lineup(df)
    st.dataframe(lineup[['Nickname', 'Position', 'Salary', 'Projection']])

    # --- 💰 Summary Stats ---
    total_salary = lineup['Salary'].sum()
    total_projection = lineup['Projection'].sum()
    st.write(f"**Total Salary:** ${total_salary}")
    st.write(f"**Total Projected Points:** {total_projection:.2f}")

else:
    st.info("Please upload a FanDuel CSV file to get started.")
