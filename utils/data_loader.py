"""
Data loading utilities for fixtures, team strength, and historical data.
All paths are relative to project root.
"""
import logging

import pandas as pd
import requests
import streamlit as st
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
FIXTURES_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"


@st.cache_data(ttl=3600, show_spinner="Loading 2026 World Cup fixtures...")
def load_fixtures() -> pd.DataFrame:
    """Load 2026 World Cup fixtures from openfootball public JSON (with fallback)."""
    try:
        resp = requests.get(FIXTURES_URL, timeout=15)
        resp.raise_for_status()
        raw = resp.json()

        matches = []
        for m in raw.get("matches", []):
            matches.append(
                {
                    "date": m.get("date"),
                    "time_utc": m.get("time"),
                    "team1": m.get("team1", "TBD"),
                    "team2": m.get("team2", "TBD"),
                    "group": m.get("group"),
                    "round": m.get("round", "Group Stage"),
                    "venue": m.get("ground", "TBD"),
                }
            )

        df = pd.DataFrame(matches)
        if df.empty:
            return _fallback_fixtures()

        # Parse datetime
        df["datetime_utc"] = df.apply(
            lambda r: pd.to_datetime(
                f"{r['date']} {str(r['time_utc']).split()[0] if pd.notna(r['time_utc']) else '00:00'}",
                errors="coerce",
            ),
            axis=1,
        )
        df["ist_time"] = df["datetime_utc"].apply(
            lambda x: (
                x.tz_localize("UTC")
                .tz_convert("Asia/Kolkata")
                .strftime("%d %b, %I:%M %p IST")
                if pd.notna(x)
                else "TBD"
            )
        )
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        return df

    except Exception as e:
        logger.error(f"Live fixtures fetch failed: {e}. Using bundled fallback data.")
        st.warning("Live fixtures fetch failed. Using bundled fallback data.")
        return _fallback_fixtures()


def _fallback_fixtures() -> pd.DataFrame:
    """Minimal fallback so the app is always usable offline."""
    data = [
        {
            "date": "2026-06-11",
            "time_utc": "18:00",
            "team1": "Mexico",
            "team2": "Argentina",
            "group": "A",
            "round": "Group Stage",
            "venue": "Mexico City",
        },
        {
            "date": "2026-06-12",
            "time_utc": "15:00",
            "team1": "USA",
            "team2": "Brazil",
            "group": "B",
            "round": "Group Stage",
            "venue": "New York",
        },
        {
            "date": "2026-06-13",
            "time_utc": "19:00",
            "team1": "France",
            "team2": "Germany",
            "group": "C",
            "round": "Group Stage",
            "venue": "Toronto",
        },
        {
            "date": "2026-06-14",
            "time_utc": "17:00",
            "team1": "England",
            "team2": "Spain",
            "group": "D",
            "round": "Group Stage",
            "venue": "Dallas",
        },
        {
            "date": "2026-06-15",
            "time_utc": "20:00",
            "team1": "Portugal",
            "team2": "Netherlands",
            "group": "E",
            "round": "Group Stage",
            "venue": "Atlanta",
        },
    ]
    df = pd.DataFrame(data)
    df["datetime_utc"] = pd.to_datetime(df["date"] + " " + df["time_utc"])
    df["ist_time"] = (
        df["datetime_utc"]
        .dt.tz_localize("UTC")
        .dt.tz_convert("Asia/Kolkata")
        .dt.strftime("%d %b, %I:%M %p IST")
    )
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


@st.cache_data(ttl=7200)
def load_team_strength() -> pd.DataFrame:
    path = DATA_DIR / "team_strength.csv"
    if path.exists():
        return pd.read_csv(path)
    # Fallback minimal strength table
    return pd.DataFrame(
        {
            "team": [
                "Argentina",
                "France",
                "Brazil",
                "England",
                "Spain",
                "Germany",
                "Portugal",
                "Mexico",
                "USA",
                "India",
            ],
            "strength": [92, 91, 90, 88, 87, 86, 85, 78, 77, 55],
            "confederation": [
                "CONMEBOL",
                "UEFA",
                "CONMEBOL",
                "UEFA",
                "UEFA",
                "UEFA",
                "UEFA",
                "CONCACAF",
                "CONCACAF",
                "AFC",
            ],
        }
    )


@st.cache_data
def load_historical_matches() -> pd.DataFrame:
    path = DATA_DIR / "historical_matches.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()  # Will trigger synthetic generation in ml_model
