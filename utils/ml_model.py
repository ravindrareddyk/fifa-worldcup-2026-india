"""
Beginner-friendly ML module for match outcome prediction.
Uses RandomForest on engineered features from team strength + context.
Model is trained on synthetic + historical data and persisted with joblib.
"""

# ruff: noqa: E402  (warnings filter must run before importing sklearn / heavy libs)
import warnings

warnings.filterwarnings("ignore")

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from .data_loader import load_team_strength, load_historical_matches

MODEL_PATH = Path(__file__).parent.parent / "data" / "wc2026_model.joblib"
DATA_DIR = Path(__file__).parent.parent / "data"


def _get_strength_dict() -> dict:
    df = load_team_strength()
    return dict(zip(df["team"], df["strength"]))


def _engineer_features(df: pd.DataFrame, strength_dict: dict) -> pd.DataFrame:
    """Create simple, interpretable features for beginners."""
    df = df.copy()
    df["team1_str"] = df["team1"].map(strength_dict).fillna(72)
    df["team2_str"] = df["team2"].map(strength_dict).fillna(72)
    df["str_diff"] = df["team1_str"] - df["team2_str"]
    df["is_knockout"] = df.get("is_knockout", 0)
    df["neutral_venue"] = df.get("neutral_venue", 1)
    # Add a little noise so students see real-world variance
    df["team1_str"] += np.random.normal(0, 1.5, len(df))
    df["team2_str"] += np.random.normal(0, 1.5, len(df))
    return df[["team1_str", "team2_str", "str_diff", "is_knockout", "neutral_venue"]]


def _prepare_training_data() -> tuple[pd.DataFrame, pd.Series]:
    hist = load_historical_matches()
    strength = _get_strength_dict()

    if hist.empty:
        # Generate synthetic training data if no historical file
        np.random.seed(42)
        teams = list(strength.keys())
        rows = []
        for _ in range(800):
            t1, t2 = np.random.choice(teams, 2, replace=False)
            is_ko = np.random.choice([0, 1], p=[0.7, 0.3])
            neutral = 1
            s1, s2 = strength[t1], strength[t2]
            # Simple outcome simulation
            exp_diff = (s1 - s2) / 12.0
            prob1 = 1 / (1 + np.exp(-exp_diff))
            outcome = np.random.choice(
                [1, 0, 2], p=[prob1 * 0.7, 0.2, (1 - prob1) * 0.7]
            )  # 1=team1 win, 0=draw, 2=team2 win
            rows.append(
                {
                    "team1": t1,
                    "team2": t2,
                    "team1_strength": s1,
                    "team2_strength": s2,
                    "is_knockout": is_ko,
                    "neutral_venue": neutral,
                    "outcome": outcome,
                }
            )
        hist = pd.DataFrame(rows)

    # Create target: 1 if team1 wins, 0 otherwise (simplified for beginners; extendable to 3-class)
    # We will predict "team1_win" vs "not" for simplicity in UI
    hist["team1_win"] = (hist["outcome"] == 1).astype(int)
    features = _engineer_features(
        hist.rename(
            columns={"team1_strength": "team1_str", "team2_strength": "team2_str"}
        ),
        strength,
    )
    target = hist["team1_win"]
    return features, target


def train_and_save_model() -> tuple[RandomForestClassifier, float]:
    """Train a simple RandomForest and persist it. Returns model + accuracy."""
    X, y = _prepare_training_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=6,
        min_samples_split=4,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    joblib.dump(model, MODEL_PATH)
    return model, round(acc, 3)


def load_model() -> RandomForestClassifier:
    """Load persisted model or train one on first use."""
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    model, _ = train_and_save_model()
    return model


def get_match_prediction(team1: str, team2: str, is_knockout: bool = False) -> dict:
    """
    Return beginner-friendly prediction for a match.
    Includes win probability, expected score range, and simple explanation.
    """
    model = load_model()
    strength = _get_strength_dict()

    row = pd.DataFrame(
        [
            {
                "team1": team1,
                "team2": team2,
                "is_knockout": int(is_knockout),
                "neutral_venue": 1,
            }
        ]
    )
    X = _engineer_features(row, strength)
    proba = model.predict_proba(X)[0]  # [P(not win), P(win)]

    p_win = float(proba[1])
    p_draw = round(max(0.12, 0.38 - abs(p_win - 0.5) * 0.4), 2)  # heuristic
    p_lose = round(1 - p_win - p_draw, 2)
    p_win = round(p_win, 2)

    # Simple expected goals heuristic (beginner friendly)
    s1 = strength.get(team1, 72)
    s2 = strength.get(team2, 72)
    base = 1.4
    exp1 = max(0.6, round(base + (s1 - s2) / 28, 1))
    exp2 = max(0.5, round(base + (s2 - s1) / 28, 1))

    # Feature importance for education
    feat_names = ["team1_str", "team2_str", "str_diff", "is_knockout", "neutral_venue"]
    importances = dict(zip(feat_names, model.feature_importances_.round(3)))

    return {
        "team1_win_prob": p_win,
        "draw_prob": p_draw,
        "team2_win_prob": p_lose,
        "expected_score": f"{exp1:.1f} - {exp2:.1f}",
        "recommended_score": (int(round(exp1)), int(round(exp2))),
        "feature_importance": importances,
        "model_note": "RandomForest (beginner model). Train on more real data for production.",
    }
