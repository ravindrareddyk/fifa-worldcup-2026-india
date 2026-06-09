"""
WC India Hub 2026 - Utility package
Clean separation of concerns for data, ML, live scores, and time handling.
"""

from .data_loader import load_fixtures, load_team_strength, load_historical_matches
from .ml_model import get_match_prediction, train_and_save_model, load_model
from .live_scores import get_live_matches, simulate_live_update
from .ist_utils import convert_to_ist
from .models import Match, PredictionResult, LeaderboardEntry, ContestSubmission
from .config import config, get_config, AppConfig

__all__ = [
    "load_fixtures",
    "load_team_strength",
    "load_historical_matches",
    "get_match_prediction",
    "train_and_save_model",
    "load_model",
    "get_model_metadata",
    "get_live_matches",
    "simulate_live_update",
    "convert_to_ist",
    "Match",
    "PredictionResult",
    "LeaderboardEntry",
    "ContestSubmission",
    "config",
    "get_config",
    "AppConfig",
]
