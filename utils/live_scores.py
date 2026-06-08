"""
Live score handling with two modes:
1. Simulated "live" matches (perfect for demos & portfolios before real tournament)
2. Real API stub (user provides FOOTBALL_API_KEY)

This teaches students graceful degradation and environment-based config.
"""

import random
import os
from .data_loader import load_fixtures


def _get_mock_live_matches() -> list[dict]:
    """Generate plausible in-progress or just-finished matches for demo."""
    base_fixtures = load_fixtures().head(8)
    statuses = ["LIVE 23'", "LIVE 41'", "LIVE 67'", "HT", "LIVE 81'", "FT", "LIVE 12'"]
    live = []

    for _, row in base_fixtures.iterrows():
        status = random.choice(statuses)
        # Simulate some goals
        g1 = random.choice([0, 0, 1, 1, 1, 2])
        g2 = (
            random.choice([0, 0, 0, 1, 1, 2])
            if status not in ["LIVE 12'"]
            else random.choice([0, 0, 1])
        )

        live.append(
            {
                "match": f"{row['team1']} vs {row['team2']}",
                "team1": row["team1"],
                "team2": row["team2"],
                "score": f"{g1} - {g2}",
                "status": status,
                "venue": row.get("venue", "TBD"),
                "ist_time": row.get("ist_time", "TBD"),
                "minute": (
                    int(status.replace("LIVE ", "").replace("'", ""))
                    if "LIVE" in status
                    else None
                ),
                "is_live": "LIVE" in status,
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
