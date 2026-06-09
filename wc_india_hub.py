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
from pathlib import Path
import logging

# -----------------------------------------------------------------------------
# Structured Logging Setup (Professional Robustness)
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("wc_india_hub")

# Internal modules
from utils.data_loader import load_fixtures, load_team_strength
from utils.ml_model import get_match_prediction, train_and_save_model, get_model_metadata
from utils.live_scores import get_live_matches, simulate_live_update
from utils.ist_utils import get_current_ist
from utils.models import ContestSubmission, LeaderboardEntry
from utils.config import config, get_config

logger.info("WC India Hub 2026 starting up...")
logger.info(f"Config loaded | env={config.env} | debug={config.debug} | log_level={config.log_level}")
# Reconfigure level if different (after config load)
logging.getLogger().setLevel(getattr(logging, config.log_level.upper(), logging.INFO))

# -----------------------------------------------------------------------------
# Page config & styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="WC India Hub 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polish (works alongside .streamlit/config.toml theme)
st.markdown(
    """
<style>
    .main .block-container { padding-top: 1.2rem; }
    .stMetric { 
        background-color: #f1f5f9; 
        border-radius: 10px; 
        padding: 10px; 
        border: 1px solid #e2e8f0;
    }
    .big-prob { font-size: 1.6rem; font-weight: 700; }
    /* Professional card-like containers */
    .stContainer {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
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
    st.caption("✅ Structured logging enabled")
    st.caption("✅ Live score simulator (demo mode)")
    st.caption("🔑 Add FOOTBALL_API_KEY for real API")

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
col_title, col_time = st.columns([3, 1])
with col_title:
    st.title("🏆 FIFA World Cup 2026 — India Hub")
    st.markdown(
        "**Live Schedule • ML Predictions • Live Scores • Fan Support** | "
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
logger.info(f"Data loaded: {len(fixtures)} fixtures, {len(team_df)} teams. Pydantic models enabled for validation.")

# -----------------------------------------------------------------------------
# Session State + SQLite Persistence for Monetization Features (Phase 2 - Robust)
# More professional than CSV: proper schema, transactions, queries.
# -----------------------------------------------------------------------------
import sqlite3

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

CONTEST_DB = DATA_DIR / "contest.db"


def _get_db_connection():
    conn = sqlite3.connect(CONTEST_DB)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    """Initialize SQLite schema if not exists."""
    with _get_db_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                points INTEGER NOT NULL CHECK (points >= 0),
                prediction TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)


_init_db()


def load_leaderboard():
    try:
        with _get_db_connection() as conn:
            rows = conn.execute(
                f"SELECT user, points, prediction FROM leaderboard ORDER BY points DESC LIMIT {config.max_leaderboard_entries}"
            ).fetchall()
            if rows:
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to load leaderboard from SQLite: {e}")

    # Default demo data (seeded once)
    defaults = [
        {"user": "Rohit_93", "points": 1240, "prediction": "France 2-1"},
        {"user": "PriyaWC", "points": 1185, "prediction": "Argentina 1-1"},
        {"user": "Amit_11", "points": 1090, "prediction": "Brazil 3-0"},
        {"user": "SanaK", "points": 1025, "prediction": "Germany 2-2"},
        {"user": "Vikram88", "points": 980, "prediction": "Spain 2-0"},
    ]
    try:
        with _get_db_connection() as conn:
            conn.executemany(
                "INSERT OR IGNORE INTO leaderboard (user, points, prediction) VALUES (?, ?, ?)",
                [(d["user"], d["points"], d["prediction"]) for d in defaults],
            )
    except Exception as e:
        logger.error(f"Failed to seed default leaderboard: {e}")
    return defaults


def save_leaderboard(data):
    """Replace current 'You (Demo)' entries and insert new top ones."""
    try:
        with _get_db_connection() as conn:
            conn.execute("DELETE FROM leaderboard WHERE user = ?", ("You (Demo)",))
            for entry in data[:10]:
                conn.execute(
                    "INSERT INTO leaderboard (user, points, prediction) VALUES (?, ?, ?)",
                    (entry["user"], entry["points"], entry["prediction"]),
                )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to save leaderboard to SQLite: {e}")


def load_subscribers():
    try:
        with _get_db_connection() as conn:
            rows = conn.execute("SELECT email FROM subscribers ORDER BY created_at DESC").fetchall()
            return [row["email"] for row in rows]
    except Exception as e:
        logger.error(f"Failed to load subscribers from SQLite: {e}")
    return []


def save_subscribers(emails):
    try:
        with _get_db_connection() as conn:
            for email in emails:
                conn.execute(
                    "INSERT OR IGNORE INTO subscribers (email) VALUES (?)", (email,)
                )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to save subscribers to SQLite: {e}")


if "subscribers" not in st.session_state:
    st.session_state.subscribers = load_subscribers()

if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = load_leaderboard()

if "my_predictions" not in st.session_state:
    st.session_state.my_predictions = []

if "claimed_rewards" not in st.session_state:
    st.session_state.claimed_rewards = []

if "last_ml_prediction" not in st.session_state:
    st.session_state.last_ml_prediction = None


# Auto-persist helper (call after mutations in monetization)
def persist_monetization_data():
    """Persist current in-memory state to SQLite (robust replacement for CSV)."""
    save_leaderboard(st.session_state.leaderboard)
    save_subscribers(st.session_state.subscribers)

# -----------------------------------------------------------------------------
# Main Tabs
# -----------------------------------------------------------------------------
tabs = st.tabs(
    [
        "📅 Schedule (IST)",
        "🔴 Live Scores",
        "🔮 ML Predictions",
        "💰 Support & Monetize",
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

        # Professional export feature
        csv_schedule = view[["date", "ist_time", "team1", "team2", "group", "round", "venue"]].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Schedule (CSV)",
            data=csv_schedule,
            file_name="wc2026_schedule.csv",
            mime="text/csv",
            key="download_schedule",
        )
    else:
        st.info("Fixtures will be available closer to the tournament (June 2026).")

# =============================================================================
# TAB 1: Live Scores (Simulated + Real API ready)
# =============================================================================
with tabs[1]:
    st.subheader("🔴 Live Scores & Match Status")
    st.caption(
        "Currently in **demo / simulation mode** using accurate 2026 WC groups & early schedule (from official FIFA draw). Real API integration ready (see utils/live_scores.py)."
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
        group = match.get("group", "")
        group_label = f" | Group {group}" if group else ""
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1.5, 1])
            with c1:
                st.markdown(f"**{match['match']}**{group_label}")
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

    # --- Group Tables & Overview (added for better accuracy) ---
    st.subheader("📊 Group Overview (Mock Standings based on real 2026 groups)")

    groups_overview = {
        "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
        "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
        "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
        "D": ["United States", "Paraguay", "Australia", "Türkiye"],
    }

    cols = st.columns(2)
    for idx, (group, teams) in enumerate(groups_overview.items()):
        with cols[idx % 2]:
            st.markdown(f"**Group {group}**")
            # Simple mock standings (P W D L GF GA GD Pts)
            standings = []
            for i, team in enumerate(teams):
                # Fake some results for demo
                p, w, d, l = 1, 1 if i == 0 else 0, 0, 0 if i == 0 else 1
                gf, ga = (2 if i == 0 else 0), (0 if i == 0 else 1)
                pts = 3 if i == 0 else 0
                standings.append([team, p, w, d, l, gf, ga, gf-ga, pts])

            stand_df = pd.DataFrame(
                standings,
                columns=["Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"],
            )
            st.dataframe(stand_df, use_container_width=True, hide_index=True)

    st.caption("Standings are illustrative/mock for demo purposes. Real groups from official 2026 draw.")

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

            # Capture for Monetize tab contest integration (Phase 2)
            st.session_state.last_ml_prediction = {
                "team1": team1,
                "team2": team2,
                "recommended_score": pred["recommended_score"],
                "win_prob": pred["team1_win_prob"],
            }

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

    # Model versioning display (professional touch)
    meta = get_model_metadata()
    st.caption(
        f"**Model Version**: {meta.get('version', 'N/A')} | "
        f"Trained: {meta.get('trained_at', 'N/A')[:19]} | "
        f"Accuracy: {meta.get('accuracy', 'N/A')}"
    )

    if st.button("🔁 Retrain Model Now (demo)"):
        with st.spinner("Retraining RandomForest..."):
            model, acc = train_and_save_model()
        logger.info(f"Model retrained via UI. Accuracy: {acc}")
        st.success(f"Model retrained! Validation accuracy ≈ {acc}")

# =============================================================================
# TAB 3: Support & Monetize (Phase 2 - Enhanced)
# =============================================================================
with tabs[3]:  # Monetize tab
    st.subheader("💰 Support the Hub & Earn Rewards")
    st.markdown(
        """
    **Thank you for using WC India Hub!**  
    Help keep this free for Indian fans & unlock exclusive rewards.
    """
    )

    # --- Impact Metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Supporters", "1,284", "+47 today")
    m2.metric("Affiliate Revenue (Demo)", "₹4,280", "This month")
    m3.metric("Predictions Shared", "3,912", "for contests")
    m4.metric("Active Contestants", str(len(st.session_state.leaderboard)), "this week")

    st.divider()

    # --- Configurable Affiliate Links (Phase 2 improvement) ---
    with st.expander("🔗 Configure Your Affiliate / Referral Links (Demo)", expanded=False):
        st.caption("Edit these in a real deployment or via st.secrets / .env")

        default_links = {
            "amazon": "https://amzn.to/your-affiliate-tag",
            "dream11": "https://dream11.com/your-ref-link",
            "zee5": "https://zee5.com",
        }

        if "affiliate_links" not in st.session_state:
            st.session_state.affiliate_links = default_links.copy()

        col_a, col_b = st.columns(2)
        with col_a:
            st.session_state.affiliate_links["amazon"] = st.text_input(
                "Amazon Affiliate Link", value=st.session_state.affiliate_links["amazon"], key="aff_amzn"
            )
            st.session_state.affiliate_links["dream11"] = st.text_input(
                "Fantasy Platform Link", value=st.session_state.affiliate_links["dream11"], key="aff_dream"
            )
        with col_b:
            st.session_state.affiliate_links["zee5"] = st.text_input(
                "Streaming Partner Link", value=st.session_state.affiliate_links["zee5"], key="aff_zee"
            )

        if st.button("Reset to Default Links"):
            st.session_state.affiliate_links = default_links.copy()
            st.rerun()

    # --- Affiliate / Partner Cards (now use configurable links) ---
    st.markdown("### 🛒 Partner Offers & Ways to Support")

    links = st.session_state.get("affiliate_links", {})

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🛍️ Shop Official Fan Gear**")
        st.markdown("Jerseys, flags, scarves & more")
        st.markdown(f"[Amazon India →]({links.get('amazon', '#')})")
        if st.button("Browse Merch", key="merch"):
            st.toast("🔗 Opening Amazon affiliate link (demo)")

    with col2:
        st.markdown("**🎯 Fantasy Leagues & Contests**")
        st.markdown("Play & win big with your WC knowledge")
        st.markdown(f"[Dream11 / MyTeam11 →]({links.get('dream11', '#')})")
        if st.button("Join Fantasy", key="fantasy"):
            st.toast("🔗 Opening fantasy platform (demo)")

    with col3:
        st.markdown("**📺 Watch Every Match Live**")
        st.markdown("Exclusive streaming for Indian viewers")
        st.markdown(f"[Zee5 / Unite8 Sports →]({links.get('zee5', '#')})")
        if st.button("Watch Live", key="watch"):
            st.toast("🔗 Opening streaming partner (demo)")

    st.caption("💡 Edit links in the expander above • Replace with your real affiliate tags in production")

    st.divider()

    # --- Community Prediction Contest + Integration ---
    st.markdown("### 🏆 Weekly Prediction Contest")
    st.markdown(
        "Submit predictions, climb the leaderboard, and earn points redeemable for rewards. "
        "Top entries can unlock partner perks and early access to better models."
    )

    # Personal stats
    user_entries = [e for e in st.session_state.leaderboard if e["user"] == "You (Demo)"]
    user_points = user_entries[0]["points"] if user_entries else 0
    user_rank = next((i+1 for i, e in enumerate(st.session_state.leaderboard) if e["user"] == "You (Demo)"), None)

    p1, p2, p3 = st.columns(3)
    p1.metric("Your Points", user_points)
    p2.metric("Your Rank", f"#{user_rank}" if user_rank else "Not ranked yet")
    p3.metric("Your Submissions", len(st.session_state.my_predictions))

    # Import from ML Predictions tab (new integration)
    if st.session_state.last_ml_prediction:
        last = st.session_state.last_ml_prediction
        if st.button(
            f"📥 Import Last ML Prediction ({last['team1']} vs {last['team2']})",
            key="import_ml",
        ):
            st.session_state["imported_pred"] = last
            st.success(
                f"Imported: {last['team1']} {last['recommended_score'][0]}-{last['recommended_score'][1]} {last['team2']} "
                f"(win prob {last['win_prob']*100:.0f}%)"
            )
            st.rerun()
    else:
        st.caption("Make a prediction in the 🔮 ML Predictions tab to import it here automatically.")

    # Leaderboard display
    if st.session_state.leaderboard:
        lb_df = pd.DataFrame(st.session_state.leaderboard)
        lb_df.insert(0, "Rank", range(1, len(lb_df) + 1))
        st.dataframe(
            lb_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "points": st.column_config.ProgressColumn("Points", min_value=0, max_value=1500),
            },
        )

        # Professional export feature
        csv = lb_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Leaderboard (CSV)",
            data=csv,
            file_name="wc2026_leaderboard.csv",
            mime="text/csv",
            key="download_leaderboard",
        )

    st.markdown("**Submit / Update your contest prediction**")

    # Team selection
    available_teams = (
        sorted(pd.unique(pd.concat([fixtures["team1"], fixtures["team2"]])).tolist())
        if not fixtures.empty
        else ["Argentina", "France", "Brazil", "Germany", "Spain"]
    )

    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        pred_team1 = st.selectbox("Team 1", available_teams, index=0, key="mon_t1")
    with sub_col2:
        remaining = [t for t in available_teams if t != pred_team1]
        default_idx = 0
        if "imported_pred" in st.session_state:
            imp = st.session_state["imported_pred"]
            if imp["team1"] == pred_team1 and imp["team2"] in remaining:
                default_idx = remaining.index(imp["team2"])
        pred_team2 = st.selectbox("Team 2", remaining, index=default_idx, key="mon_t2")

    # Auto-fill from imported or get new ML rec
    imported = st.session_state.get("imported_pred")
    use_imported = False
    if imported and imported["team1"] == pred_team1 and imported["team2"] == pred_team2:
        use_imported = True
        default_s1, default_s2 = imported["recommended_score"]
    else:
        default_s1, default_s2 = 1, 1

    # ML button
    if st.button("🤖 Get Fresh ML Recommendation", key="get_ml_rec"):
        ml_pred = get_match_prediction(pred_team1, pred_team2)
        st.session_state[f"ml_rec_{pred_team1}_{pred_team2}"] = ml_pred
        st.success(
            f"ML suggests **{pred_team1} {ml_pred['recommended_score'][0]} - "
            f"{ml_pred['recommended_score'][1]} {pred_team2}** "
            f"(Win prob: {ml_pred['team1_win_prob']*100:.0f}%)"
        )

    rec = st.session_state.get(f"ml_rec_{pred_team1}_{pred_team2}", {})
    if use_imported and not rec:
        rec = {"recommended_score": (default_s1, default_s2)}

    s1 = st.slider(f"{pred_team1} goals", 0, 5, rec.get("recommended_score", (default_s1, default_s2))[0], key=f"s1_{pred_team1}")
    s2 = st.slider(f"{pred_team2} goals", 0, 5, rec.get("recommended_score", (default_s1, default_s2))[1], key=f"s2_{pred_team2}")

    if st.button("🚀 Submit / Update Prediction", type="primary", key="submit_pred"):
        points = 50 + abs(3 - abs(s1 - s2)) * 15
        if rec or use_imported:
            points += 30  # ML bonus

        # Use Pydantic for validation (robustness)
        try:
            submission = ContestSubmission(
                team1=pred_team1,
                team2=pred_team2,
                score1=s1,
                score2=s2,
                points_earned=points,
            )
            entry: LeaderboardEntry = submission.to_leaderboard_entry()
        except Exception as e:
            logger.error(f"Invalid submission: {e}")
            st.error(f"Invalid prediction data: {e}")
            st.stop()

        st.session_state.leaderboard = [
            e for e in st.session_state.leaderboard if e["user"] != "You (Demo)"
        ]
        st.session_state.leaderboard.append(entry.model_dump())
        st.session_state.leaderboard.sort(key=lambda x: x["points"], reverse=True)
        st.session_state.leaderboard = st.session_state.leaderboard[: config.max_leaderboard_entries]

        if entry.prediction not in st.session_state.my_predictions:
            st.session_state.my_predictions.append(entry.prediction)

        persist_monetization_data()

        logger.info(f"User submitted prediction: {entry.prediction} for {points} points")
        st.success(f"✅ Submitted! Earned **{points} points**. Leaderboard updated (SQLite).")
        st.balloons()
        st.rerun()

    st.caption("💡 Using ML recommendation or imported prediction = bonus points. Data persisted to SQLite (data/contest.db) for robustness.")

    # --- Rewards / Claim System (new Phase 2 feature) ---
    st.divider()
    st.markdown("### 🎁 Rewards Shop (Redeem Your Points)")

    REWARDS = [
        {"name": "🏆 Contest Shoutout", "cost": 120, "desc": "Get featured in the next weekly recap"},
        {"name": "📊 Advanced Stats Access", "cost": 250, "desc": "Early peek at model confidence intervals"},
        {"name": "🛍️ 15% Merch Discount Code", "cost": 380, "desc": "One-time code for Amazon affiliate store"},
        {"name": "🎟️ Fantasy Entry Credit", "cost": 450, "desc": "₹50 equivalent credit on partner platform"},
        {"name": "🌟 Premium Model Beta", "cost": 650, "desc": "Access to next version of the ML predictor"},
    ]

    for reward in REWARDS:
        col_r1, col_r2 = st.columns([3, 1])
        with col_r1:
            st.markdown(f"**{reward['name']}** — {reward['cost']} pts")
            st.caption(reward["desc"])
        with col_r2:
            already_claimed = reward["name"] in st.session_state.claimed_rewards
            if already_claimed:
                st.success("Claimed ✓")
            elif user_points >= reward["cost"]:
                if st.button(f"Claim ({reward['cost']} pts)", key=f"claim_{reward['name']}"):
                    st.session_state.claimed_rewards.append(reward["name"])
                    # Optional: deduct points from user's entry
                    for e in st.session_state.leaderboard:
                        if e["user"] == "You (Demo)":
                            e["points"] -= reward["cost"]
                            break
                    persist_monetization_data()
                    st.success(f"Redeemed: {reward['name']}")
                    st.rerun()
            else:
                st.button(f"Need {reward['cost'] - user_points} more", disabled=True, key=f"need_{reward['name']}")

    if st.session_state.claimed_rewards:
        st.markdown("**Your claimed rewards:** " + " • ".join(st.session_state.claimed_rewards))

    # --- Newsletter / Lead Gen ---
    st.divider()
    with st.expander("📬 Get Daily WC Tips, Analysis & Contest Updates (Free)", expanded=True):
        email = st.text_input("Your email address", placeholder="fan@example.com", key="newsletter_email")
        if st.button("Join Free Community", key="join_newsletter", type="primary"):
            if email and "@" in email:
                if email not in st.session_state.subscribers:
                    st.session_state.subscribers.append(email)
                    persist_monetization_data()
                logger.info(f"New subscriber added: {email}")
                st.success(f"🎉 Welcome! Tips & contest alerts will be sent to {email}.")
            else:
                st.warning("Please enter a valid email.")

        if st.session_state.subscribers:
            st.write("**Recent members:** " + ", ".join(st.session_state.subscribers[-5:]))
            st.caption(f"Total: **{len(st.session_state.subscribers)}** subscribers")

    # --- My History + Admin Tools ---
    with st.expander("📋 My Submissions & Demo Controls"):
        if st.session_state.my_predictions:
            st.write("Your recent predictions:")
            for p in st.session_state.my_predictions[-6:][::-1]:
                st.write(f"• {p}")
        else:
            st.caption("No submissions yet.")

        if st.button("🗑️ Reset All Demo Data (Leaderboard, Subscribers, Rewards)"):
            st.session_state.leaderboard = load_leaderboard()  # reset to defaults
            st.session_state.subscribers = []
            st.session_state.my_predictions = []
            st.session_state.claimed_rewards = []
            st.session_state.last_ml_prediction = None
            if "imported_pred" in st.session_state:
                del st.session_state["imported_pred"]
            # Clear SQLite tables (robust reset)
            try:
                with _get_db_connection() as conn:
                    conn.execute("DELETE FROM leaderboard")
                    conn.execute("DELETE FROM subscribers")
                    conn.commit()
            except Exception as e:
                logger.error(f"Failed to reset SQLite contest DB: {e}")
            st.success("Demo data reset (SQLite + session).")
            st.rerun()

    # --- Educational note ---
    st.markdown(
        """
    ---
    **Teaching notes (Monetization & Engagement patterns):**
    - Configurable links + session_state make the demo easy to customize live.
    - Cross-tab state (`last_ml_prediction`) shows how to connect features without a database.
    - SQLite persistence (replacing earlier CSV) demonstrates a more robust “local database” pattern with schema and transactions.
    - Gamified points + redeemable rewards = higher retention (classic freemium tactic).
    - Email capture + contest = two powerful levers for future monetization (sponsors, premium tier, merch).
    """
    )

# =============================================================================
# TAB 4: Analytics
# =============================================================================
with tabs[4]:
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
# TAB 5: For Students & Faculty (Teaching tab)
# =============================================================================
with tabs[5]:
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
