"""
Basic smoke tests for the project.
Run with: pytest
"""

import pandas as pd
from utils.data_loader import load_team_strength, load_fixtures
from utils.ml_model import get_match_prediction, load_model


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
