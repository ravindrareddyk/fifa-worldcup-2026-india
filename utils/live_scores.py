"""
Live score handling with two modes:
1. Simulated "live" matches (perfect for demos & portfolios before real tournament)
2. Real API stub (user provides FOOTBALL_API_KEY)

This teaches students graceful degradation and environment-based config.
"""
import logging
import random
import os

from .data_loader import load_fixtures

logger = logging.getLogger(__name__)


def _get_mock_live_matches() -> list[dict]:
    """Generate plausible in-progress or just-finished matches for demo.
    Uses accurate 2026 WC groups and early schedule (researched from official FIFA sources)
    for realistic data instead of random outdated fixtures.
    """
    # Curated list of real early Group Stage matches from the official 2026 schedule
    # (sourced from FIFA official schedule and draw - June 11-14 2026 window)
    # Added approximate IST times for Indian fans (times can shift slightly)
    realistic_early_matches = [
        {"team1": "Mexico", "team2": "South Africa", "group": "A", "venue": "Mexico City Stadium", "ist_time": "12 Jun, 06:30 AM IST"},
        {"team1": "South Korea", "team2": "Czechia", "group": "A", "venue": "Guadalajara Stadium", "ist_time": "12 Jun, 01:30 PM IST"},
        {"team1": "Canada", "team2": "Bosnia and Herzegovina", "group": "B", "venue": "BMO Field, Toronto", "ist_time": "12 Jun, 10:30 PM IST"},
        {"team1": "Qatar", "team2": "Switzerland", "group": "B", "venue": "Levi's Stadium", "ist_time": "13 Jun, 08:30 AM IST"},
        {"team1": "Brazil", "team2": "Morocco", "group": "C", "venue": "MetLife Stadium, NY/NJ", "ist_time": "14 Jun, 08:30 AM IST"},
        {"team1": "Haiti", "team2": "Scotland", "group": "C", "venue": "Hard Rock Stadium, Miami", "ist_time": "14 Jun, 11:30 AM IST"},
        {"team1": "United States", "team2": "Paraguay", "group": "D", "venue": "SoFi Stadium, Los Angeles", "ist_time": "13 Jun, 11:30 AM IST"},
        {"team1": "Australia", "team2": "Türkiye", "group": "D", "venue": "AT&T Stadium, Dallas", "ist_time": "14 Jun, 03:30 PM IST"},
    ]

    # More realistic status options for group stage openers
    statuses = ["LIVE 23'", "LIVE 41'", "LIVE 58'", "HT", "LIVE 72'", "LIVE 81'", "FT", "LIVE 12'"]

    live = []
    for i, match_info in enumerate(realistic_early_matches):
        # Make status more realistic for the actual schedule
        # First match (Mexico opener) should not be "HT" or "FT" if it's the very first game
        if i == 0:
            status = random.choice(["LIVE 12'", "LIVE 23'", "LIVE 35'"])
        else:
            status = random.choice(statuses)

        # Better goal simulation (low scoring for openers + home/co-host bias)
        home_teams = ["Mexico", "Canada", "United States", "Brazil"]
        if match_info["team1"] in home_teams:
            g1 = random.choice([1, 1, 2, 2, 3])
            g2 = random.choice([0, 0, 1, 1, 2])
        else:
            g1 = random.choice([0, 0, 1, 1, 1, 2])
            g2 = random.choice([0, 0, 1, 1, 2])

        if random.random() < 0.35:  # occasional away result
            g1, g2 = g2, g1

        live.append(
            {
                "match": f"{match_info['team1']} vs {match_info['team2']}",
                "team1": match_info["team1"],
                "team2": match_info["team2"],
                "score": f"{g1} - {g2}",
                "status": status,
                "venue": match_info["venue"],
                "ist_time": match_info.get("ist_time", "TBD (see Schedule tab)"),
                "minute": (
                    int(status.replace("LIVE ", "").replace("'", ""))
                    if "LIVE" in status
                    else None
                ),
                "is_live": "LIVE" in status,
                "group": match_info["group"],
            }
        )
    return live


def get_live_matches(use_real_api: bool = False) -> list[dict]:
    """
    Main entry point.
    If FOOTBALL_API_KEY is set and use_real_api=True, try real provider.
    Otherwise return simulated live matches.
    """
    api_key = os.getenv("FOOTBALL_API_KEY") or os.getenv("API_FOOTBALL_KEY")

    if use_real_api and api_key:
        try:
            return _fetch_from_football_api(api_key)
        except Exception as e:
            logger.error(f"Real live scores API failed: {e}")
            return [
                {
                    "match": "API Error",
                    "score": "N/A",
                    "status": str(e)[:60],
                    "is_live": False,
                }
            ]

    # Default: beautiful simulated data for demos
    return _get_mock_live_matches()


def _fetch_from_football_api(api_key: str) -> list[dict]:
    """
    Stub for real integration (e.g. api.football-data.org or api-sports.io).
    Students can extend this function.
    """
    # Placeholder - real implementation would do requests.get with headers
    # For now we return a clear message so the UI stays usable.
    return [
        {
            "match": "Real API not fully wired yet",
            "team1": "See docs",
            "team2": "Add your key",
            "score": "—",
            "status": "Configure FOOTBALL_API_KEY env var",
            "is_live": False,
            "note": "Good student exercise: implement _fetch_from_football_api()",
        }
    ]


def simulate_live_update(current_matches: list[dict]) -> list[dict]:
    """Mutate scores for 'live' feel when user clicks refresh (demo only)."""
    updated = []
    for m in current_matches:
        if not m.get("is_live"):
            updated.append(m)
            continue

        g1, g2 = map(int, m["score"].split(" - "))
        # Small chance of a goal
        if random.random() < 0.35:
            g1 += random.choice([0, 1])
        if random.random() < 0.28:
            g2 += random.choice([0, 1])
        m["score"] = f"{g1} - {g2}"
        m["status"] = f"LIVE {random.randint(25, 88)}'"
        updated.append(m)
    return updated
