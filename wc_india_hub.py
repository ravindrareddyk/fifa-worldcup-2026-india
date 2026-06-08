"""
WC India Hub 2026 - Professional Streamlit App
FIFA World Cup 2026 fan experience for Indian supporters.

Features:
- Accurate IST schedule from public openfootball data
- Real ML model (RandomForest) for match predictions
- Simulated Live Scores (with one-click "goal" simulation)
- Educational / portfolio focus for IT faculty & students

Run:
    streamlit run wc_india_hub.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Internal modules
from utils.data_loader import load_fixtures, load_team_strength
from utils.ml_model import get_match_prediction, train_and_save_model
from utils.live_scores import get_live_matches, simulate_live_update
from utils.ist_utils import get_current_ist

# -----------------------------------------------------------------------------
# Page config & styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="WC India Hub 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polish
st.markdown(
    """
<style>
    .main .block-container { padding-top: 1.2rem; }
    .stMetric { background-color: #0f172a; border-radius: 8px; padding: 8px; }
    .big-prob { font-size: 1.6rem; font-weight: 700; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
st.sidebar.header("🇮🇳 WC India Hub 2026")
st.sidebar.markdown("**For Indian Fans • IST Times**")
st.sidebar.markdown("Streaming: **Zee5 / Unite8 Sports**")

st.sidebar.divider()
st.sidebar.caption("Built by Indian IT Faculty\nas a teaching + portfolio project")

with st.sidebar.expander("⚙️ DevOps & ML Status"):
    st.caption("✅ Docker + GitHub Actions (GHCR)")
    st.caption("✅ scikit-learn RandomForest model")
    st.caption("✅ Live score simulator (demo mode)")
    st.caption("🔑 Add FOOTBALL_API_KEY for real API")

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
col_title, col_time = st.columns([3, 1])
with col_title:
    st.title("🏆 FIFA World Cup 2026 — India Hub")
    st.markdown(
        "**Live Schedule • ML Predictions • Simulated Live Scores** | "
        "Built for Indian fans by IT Faculty"
    )
with col_time:
    now_ist = get_current_ist()
    st.metric("Current IST", now_ist.strftime("%d %b %Y, %I:%M %p"))

# -----------------------------------------------------------------------------
# Data loading (cached in utils)
# -----------------------------------------------------------------------------
fixtures = load_fixtures()
team_df = load_team_strength()

# -----------------------------------------------------------------------------
# Main Tabs
# -----------------------------------------------------------------------------
tabs = st.tabs(
    [
        "📅 Schedule (IST)",
        "🔴 Live Scores",
        "🔮 ML Predictions",
        "📊 Analytics",
        "🧑‍🏫 For Students & Faculty",
    ]
)

# =============================================================================
# TAB 0: Schedule
# =============================================================================
with tabs[0]:
    st.subheader("📅 Full Schedule — All times in IST")

    if not fixtures.empty:
        today = datetime.now().date()
        upcoming = fixtures[pd.to_datetime(fixtures["date"]).dt.date >= today].copy()

        # Nice filters
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            groups = ["All"] + sorted([g for g in fixtures["group"].dropna().unique()])
            group_filter = st.selectbox("Filter by Group", groups, index=0)
        with col_f2:
            rounds = ["All"] + sorted(fixtures["round"].dropna().unique().tolist())
            round_filter = st.selectbox("Filter by Round", rounds, index=0)

        view = upcoming.copy()
        if group_filter != "All":
            view = view[view["group"] == group_filter]
        if round_filter != "All":
            view = view[view["round"] == round_filter]

        st.dataframe(
            view[["date", "ist_time", "team1", "team2", "group", "round", "venue"]],
            use_container_width=True,
            height=520,
            hide_index=True,
        )
        st.caption(
            f"Source: openfootball/worldcup.json (2026) • {len(view)} matches shown"
        )
    else:
        st.info("Fixtures will be available closer to the tournament (June 2026).")

# =============================================================================
# TAB 1: Live Scores (Simulated + Real API ready)
# =============================================================================
with tabs[1]:
    st.subheader("🔴 Live Scores & Match Status")
    st.caption(
        "Currently in **demo / simulation mode**. Real API integration ready (see utils/live_scores.py)."
    )

    # Session state for "live" simulation
    if "live_matches" not in st.session_state:
        st.session_state.live_matches = get_live_matches(use_real_api=False)

    col_l1, col_l2, col_l3 = st.columns([1, 1, 2])
    with col_l1:
        if st.button("🔄 Refresh / Simulate Goals", type="primary"):
            st.session_state.live_matches = simulate_live_update(
                st.session_state.live_matches
            )
            st.rerun()
    with col_l2:
        use_real = st.toggle(
            "Try Real API (needs key)",
            value=False,
            disabled=True,
            help="Set FOOTBALL_API_KEY env var to enable. Currently shows stub.",
        )
    with col_l3:
        st.caption("Click refresh to see 'goals' scored in real time (demo).")

    live_data = st.session_state.live_matches

    # Display as nice cards
    for match in live_data:
        status_color = "🟢" if match.get("is_live") else "⚪"
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1.5, 1])
            with c1:
                st.markdown(f"**{match['match']}**")
                st.caption(f"{match.get('venue', 'TBD')} • {match.get('ist_time', '')}")
            with c2:
                st.markdown(
                    f"<span style='font-size:1.5rem; font-weight:700'>{match['score']}</span>",
                    unsafe_allow_html=True,
                )
            with c3:
                st.markdown(f"{status_color} **{match['status']}**")

    st.info(
        "💡 **Teaching note**: This is a classic pattern — graceful fallback + simulation for demos + real integration behind a feature flag."
    )

# =============================================================================
# TAB 2: ML Predictions (Real model!)
# =============================================================================
with tabs[2]:
    st.subheader("🔮 ML-Powered Match Predictions")
    st.markdown(
        "Beginner-level **RandomForest** model trained on team strength + historical patterns."
    )

    if fixtures.empty:
        st.warning("No teams loaded. Using default list.")
        teams = sorted(team_df["team"].tolist())
    else:
        teams = sorted(
            pd.unique(pd.concat([fixtures["team1"], fixtures["team2"]])).tolist()
        )

    col_a, col_b = st.columns(2)
    with col_a:
        team1 = st.selectbox(
            "Team 1 (Home/First)",
            teams,
            index=teams.index("Argentina") if "Argentina" in teams else 0,
        )
    with col_b:
        default_team2 = "France" if "France" in teams else teams[1]
        team2 = st.selectbox(
            "Team 2",
            [t for t in teams if t != team1],
            index=0 if default_team2 != team1 else 1,
        )

    is_knockout = st.checkbox("Knockout stage match (no draws)", value=False)

    if st.button("🚀 Predict with ML Model", type="primary"):
        with st.spinner("Running model..."):
            pred = get_match_prediction(team1, team2, is_knockout=is_knockout)

        st.divider()

        # Big probability display
        m1, m2, m3 = st.columns(3)
        m1.metric(f"{team1} Win", f"{pred['team1_win_prob']*100:.0f}%")
        m2.metric("Draw", f"{pred['draw_prob']*100:.0f}%")
        m3.metric(f"{team2} Win", f"{pred['team2_win_prob']*100:.0f}%")

        st.success(
            f"**Model recommended score**: {pred['expected_score']} (approx. {pred['recommended_score'][0]}–{pred['recommended_score'][1]})"
        )

        # Feature importance (educational)
        with st.expander("📈 Why did the model decide this? (Feature Importance)"):
            imp = pred["feature_importance"]
            fig_imp = px.bar(
                x=list(imp.values()),
                y=list(imp.keys()),
                orientation="h",
                title="Feature Importance (RandomForest)",
                labels={"x": "Importance", "y": "Feature"},
            )
            st.plotly_chart(fig_imp, use_container_width=True)
            st.caption(pred["model_note"])

        # Manual override for fun / teaching
        with st.expander("Manual Score Override (for comparison)"):
            s1 = st.slider(f"{team1} goals", 0, 5, pred["recommended_score"][0])
            s2 = st.slider(f"{team2} goals", 0, 5, pred["recommended_score"][1])
            st.write(f"Your manual prediction: **{team1} {s1} - {s2} {team2}**")

    st.divider()
    st.caption(
        "Model is retrained automatically on first run or via `python -m utils.train_model`. See `data/historical_matches.csv` and `utils/ml_model.py`."
    )

    if st.button("🔁 Retrain Model Now (demo)"):
        with st.spinner("Retraining RandomForest..."):
            model, acc = train_and_save_model()
        st.success(f"Model retrained! Validation accuracy ≈ {acc}")

# =============================================================================
# TAB 3: Analytics
# =============================================================================
with tabs[3]:
    st.subheader("📊 Tournament Analytics")

    if not fixtures.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Matches per Group**")
            group_counts = fixtures["group"].value_counts().reset_index()
            group_counts.columns = ["Group", "Matches"]
            fig = px.bar(group_counts, x="Group", y="Matches", color="Group")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Teams by Strength (Top 15)**")
            top = team_df.sort_values("strength", ascending=False).head(15)
            fig2 = px.bar(top, x="team", y="strength", color="confederation")
            st.plotly_chart(fig2, use_container_width=True)

        # Strength distribution
        st.markdown("**Team Strength Distribution**")
        fig3 = px.histogram(
            team_df, x="strength", nbins=15, title="How strong are the teams?"
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Analytics will appear once real fixtures are loaded.")

# =============================================================================
# TAB 4: For Students & Faculty (Teaching tab)
# =============================================================================
with tabs[4]:
    st.subheader("🧑‍🏫 Educational Lab — Perfect for Teaching DevOps + ML + Web Apps")

    st.markdown("""
    ### Why this project exists
    This repository was intentionally designed as a **complete, realistic, yet beginner-friendly** 
    full-stack Python project for Indian engineering students and faculty.

    ### What students can learn here
    - **Python packaging & clean code**: `utils/` package with clear responsibilities
    - **Machine Learning (beginner)**: Feature engineering, RandomForest, model persistence, probability outputs
    - **MLOps basics**: Training script, model artifact, retraining in CI
    - **DevOps**: Multi-stage thinking via Docker (non-root, healthchecks, labels), GitHub Actions with GHCR
    - **Data engineering**: Robust data loading with fallbacks + caching
    - **Frontend (no JS)**: Professional Streamlit patterns (tabs, session state, metrics, expanders)
    - **API integration patterns**: Simulated live data + real API stub with env var

    ### Suggested student tasks
    1. Add more real historical World Cup data to `data/historical_matches.csv`
    2. Improve the ML model (add more features, try XGBoost/LightGBM, use 3-class outcome)
    3. Wire up a real football API in `utils/live_scores.py`
    4. Add user authentication + prediction leaderboard (Supabase / Firebase)
    5. Deploy to Railway / Fly.io / Streamlit Cloud and document the pipeline
    6. Add proper unit + integration tests

    ### Folder responsibilities
    - `wc_india_hub.py` — only UI and orchestration
    - `utils/` — all business logic (testable)
    - `data/` — versioned datasets + trained models
    - `notebooks/` — exploration & experiments (do not put production logic here)
    - `.github/workflows/` — CI/CD that actually does something useful
    """)

    st.divider()
    st.caption(
        "Made with ❤️ by Indian IT Faculty | Share on LinkedIn, X, and Instagram • @wcindiahub2026"
    )

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.divider()
st.caption(
    "Data sources: openfootball • Synthetic training data for education • "
    "This is a portfolio / teaching project — not affiliated with FIFA."
)
