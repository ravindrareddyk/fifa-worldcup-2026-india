"""
Basic smoke tests for the project.
Run with: pytest

Expanded in Phase 2 with monetization, Pydantic validation, config, and robustness tests.
"""
import pandas as pd
import pytest

from utils.data_loader import load_team_strength, load_fixtures
from utils.ml_model import get_match_prediction, load_model
from utils.models import ContestSubmission, LeaderboardEntry, PredictionResult
from utils.config import config, get_config


def test_team_strength_loads():
    df = load_team_strength()
    assert not df.empty
    assert "team" in df.columns
    assert "strength" in df.columns


def test_fixtures_loads_or_fallback():
    df = load_fixtures()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "team1" in df.columns and "team2" in df.columns


def test_ml_prediction_runs():
    model = load_model()
    assert model is not None
    pred = get_match_prediction("Argentina", "France")
    assert "team1_win_prob" in pred
    assert 0 <= pred["team1_win_prob"] <= 1
    assert "expected_score" in pred


# --- Phase 2: Robustness & Professionalism Tests ---


def test_pydantic_models_validate_correctly():
    # PredictionResult from ML
    pred_result = PredictionResult(
        team1_win_prob=0.65,
        draw_prob=0.2,
        team2_win_prob=0.15,
        expected_score="1.8 - 1.2",
        recommended_score=(2, 1),
        feature_importance={"team1_str": 0.4},
    )
    assert pred_result.team1_win_prob == 0.65

    # ContestSubmission + to_leaderboard
    sub = ContestSubmission(
        team1="Brazil", team2="Germany", score1=2, score2=1, points_earned=95
    )
    entry: LeaderboardEntry = sub.to_leaderboard_entry()
    assert entry.user == "You (Demo)"
    assert "Brazil 2-1 Germany" in entry.prediction
    assert entry.points == 95


def test_config_loads_with_defaults_and_env():
    assert config.max_leaderboard_entries > 0
    assert isinstance(config.debug, bool)
    assert config.football_api_key is None or isinstance(config.football_api_key, str)
    cfg = get_config()
    assert cfg is config  # singleton style


def test_monetization_config_values():
    assert config.points_base == 50
    assert config.points_ml_bonus == 30


def test_contest_submission_validation_rejects_bad_data():
    with pytest.raises(Exception):  # Pydantic ValidationError
        ContestSubmission(
            team1="A", team2="B", score1=10, score2=0, points_earned=10
        )


def test_config_uses_env_override(monkeypatch):
    monkeypatch.setenv("MAX_LEADERBOARD_ENTRIES", "15")
    # Re-instantiate for test (in real app it's module level at import)
    from utils.config import AppConfig
    test_cfg = AppConfig()
    assert test_cfg.max_leaderboard_entries == 15
