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
        # IST date for better display to Indian fans (accounts for time zone crossing)
        df["ist_date"] = df["datetime_utc"].apply(
            lambda x: (
                x.tz_localize("UTC").tz_convert("Asia/Kolkata").date()
                if pd.notna(x)
                else None
            )
        )
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        return df

    except Exception as e:
        logger.error(f"Live fixtures fetch failed: {e}. Using bundled fallback data.")
        st.warning("Live fixtures fetch failed. Using bundled fallback data.")
        return _fallback_fixtures()


def _fallback_fixtures() -> pd.DataFrame:
    """Minimal fallback so the app is always usable offline.
    Updated with accurate 2026 World Cup 48-team groups and early match schedule
    (based on official FIFA draw and published schedule).
    """
    data = [
        # Group A opening matches
        {
            "date": "2026-06-11",
            "time_utc": "20:00",
            "team1": "Mexico",
            "team2": "South Africa",
            "group": "A",
            "round": "Group Stage",
            "venue": "Mexico City Stadium",
        },
        {
            "date": "2026-06-12",
            "time_utc": "03:00",
            "team1": "South Korea",
            "team2": "Czechia",
            "group": "A",
            "round": "Group Stage",
            "venue": "Guadalajara Stadium",
        },
        # Group B
        {
            "date": "2026-06-12",
            "time_utc": "20:00",
            "team1": "Canada",
            "team2": "Bosnia and Herzegovina",
            "group": "B",
            "round": "Group Stage",
            "venue": "BMO Field, Toronto",
        },
        {
            "date": "2026-06-13",
            "time_utc": "20:00",
            "team1": "Qatar",
            "team2": "Switzerland",
            "group": "B",
            "round": "Group Stage",
            "venue": "Levi's Stadium, Santa Clara",
        },
        # Group C
        {
            "date": "2026-06-13",
            "time_utc": "23:00",
            "team1": "Brazil",
            "team2": "Morocco",
            "group": "C",
            "round": "Group Stage",
            "venue": "MetLife Stadium, New York/New Jersey",
        },
        {
            "date": "2026-06-14",
            "time_utc": "02:00",
            "team1": "Haiti",
            "team2": "Scotland",
            "group": "C",
            "round": "Group Stage",
            "venue": "Hard Rock Stadium, Miami",
        },
        # Group D - USA opening
        {
            "date": "2026-06-13",
            "time_utc": "02:00",
            "team1": "United States",
            "team2": "Paraguay",
            "group": "D",
            "round": "Group Stage",
            "venue": "SoFi Stadium, Los Angeles",
        },
        {
            "date": "2026-06-14",
            "time_utc": "05:00",
            "team1": "Australia",
            "team2": "Türkiye",
            "group": "D",
            "round": "Group Stage",
            "venue": "AT&T Stadium, Dallas",
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
    # Compute IST date for Indian audience (first match 11 June local = 12 June IST)
    df["ist_date"] = (
        df["datetime_utc"]
        .dt.tz_localize("UTC")
        .dt.tz_convert("Asia/Kolkata")
        .dt.date
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
