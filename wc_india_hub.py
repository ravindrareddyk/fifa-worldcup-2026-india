import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import plotly.express as px

st.set_page_config(page_title="WC India Hub 2026", layout="wide", page_icon="🏆")

st.title("🏆 FIFA World Cup 2026 - India Hub")
st.markdown("**Live Schedule • IST Timings • Predictions • Analytics** | Built by Indian IT Faculty")

# Sidebar
st.sidebar.header("🇮🇳 For Indian Fans")
st.sidebar.markdown("**Streaming:** Zee5 / Unite8 Sports")
st.sidebar.markdown("**Match Times:** Shown in IST")

@st.cache_data(ttl=3600)
def load_fixtures():
    try:
        url = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
        response = requests.get(url)
        data = response.json()
        
        matches = []
        for match in data.get("matches", []):
            matches.append({
                "Date": match.get("date"),
                "Time_UTC": match.get("time"),
                "Team1": match.get("team1", "TBD"),
                "Team2": match.get("team2", "TBD"),
                "Group": match.get("group"),
                "Round": match.get("round"),
                "Venue": match.get("ground", "TBD")
            })
        
        df = pd.DataFrame(matches)
        if not df.empty:
            # Improved datetime parsing
            df["DateTime_UTC"] = pd.to_datetime(
                df["Date"] + " " + df["Time_UTC"].str.extract(r'(\d{2}:\d{2})')[0],
                format='%Y-%m-%d %H:%M', errors='coerce'
            )
            ist = pytz.timezone('Asia/Kolkata')
            df["IST_Time"] = df["DateTime_UTC"].dt.tz_localize('UTC').dt.tz_convert(ist).dt.strftime('%d %b, %I:%M %p IST')
        return df
    except Exception as e:
        st.error(f"Fixtures loading error: {e}. Using fallback.")
        return pd.DataFrame()

fixtures = load_fixtures()

tabs = st.tabs(["📅 Schedule", "🔮 Predictions & ML", "📊 Analytics", "💰 Monetize", "🧑‍🏫 For Students"])

with tabs[0]:
    st.subheader("Upcoming Matches (IST)")
    if not fixtures.empty:
        today = datetime.now(pytz.timezone('Asia/Kolkata')).date()
        upcoming = fixtures[pd.to_datetime(fixtures["Date"]).dt.date >= today].sort_values("Date")
        st.dataframe(upcoming[["Date", "IST_Time", "Team1", "Team2", "Group", "Round", "Venue"]], use_container_width=True, height=500)
        
        group_filter = st.selectbox("Filter Group", ["All"] + sorted(fixtures["Group"].dropna().unique()))
        if group_filter != "All":
            st.dataframe(upcoming[upcoming["Group"] == group_filter], use_container_width=True)

with tabs[1]:
    st.subheader("Make Predictions + Simple ML")
    col1, col2 = st.columns(2)
    with col1: team1 = st.selectbox("Team 1", fixtures["Team1"].unique() if not fixtures.empty else [])
    with col2: team2 = st.selectbox("Team 2", fixtures["Team2"].unique() if not fixtures.empty else [])
    
    score1 = st.slider("Predicted Score Team1", 0, 5, 2)
    score2 = st.slider("Predicted Score Team2", 0, 5, 1)
    st.success(f"**Prediction:** {team1} {score1} - {score2} {team2}")
    
    st.info("🔬 **ML Model Coming** – Historical data + scikit-learn (see notebooks/)")

with tabs[2]:
    st.subheader("Tournament Analytics")
    if not fixtures.empty:
        fig = px.bar(fixtures["Group"].value_counts(), title="Matches per Group")
        st.plotly_chart(fig, use_container_width=True)

with tabs[3]:
    st.subheader("💰 Monetization")
    st.markdown("**Affiliate Links • AdSense • Premium Predictions**")
    st.button("Join Leaderboard & Get Updates")

with tabs[4]:
    st.subheader("Educational Lab Tasks")
    st.markdown("Python exercises using this data (see `/docs` and `/notebooks`)")

st.caption("Portfolio Project by Ravi | IT Faculty → DevOps / MLOps | Share on LinkedIn & Instagram @wcindiahub2026")