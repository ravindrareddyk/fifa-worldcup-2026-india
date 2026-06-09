"""
Pydantic models for data validation (Phase 2 Professionalism & Robustness).
Provides type safety and validation for predictions, leaderboard, matches, etc.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date


class Match(BaseModel):
    """Validated match/fixture data."""
    date: date
    team1: str = Field(min_length=2, max_length=30)
    team2: str = Field(min_length=2, max_length=30)
    group: Optional[str] = None
    round: str = "Group Stage"
    venue: str = "TBD"
    ist_time: str = "TBD"

    @field_validator("team1", "team2")
    @classmethod
    def validate_team(cls, v: str) -> str:
        if v in ["TBD", ""]:
            raise ValueError("Team name cannot be TBD or empty")
        return v.strip()


class PredictionResult(BaseModel):
    """Output from the ML prediction model."""
    team1_win_prob: float = Field(ge=0.0, le=1.0)
    draw_prob: float = Field(ge=0.0, le=1.0)
    team2_win_prob: float = Field(ge=0.0, le=1.0)
    expected_score: str
    recommended_score: tuple[int, int]
    feature_importance: dict[str, float]

    @field_validator("recommended_score")
    @classmethod
    def validate_score(cls, v: tuple[int, int]) -> tuple[int, int]:
        if not (0 <= v[0] <= 5 and 0 <= v[1] <= 5):
            raise ValueError("Recommended scores must be between 0 and 5")
        return v


class LeaderboardEntry(BaseModel):
    """Entry in the prediction contest leaderboard."""
    user: str = Field(min_length=1, max_length=30)
    points: int = Field(ge=0, le=2000)
    prediction: str = Field(min_length=5, max_length=50)

    @field_validator("prediction")
    @classmethod
    def validate_prediction_format(cls, v: str) -> str:
        # Simple format check: "Team1 X-Y Team2"
        parts = v.split()
        if len(parts) < 3:
            raise ValueError("Prediction must be in format 'Team1 score-team2'")
        return v


class ContestSubmission(BaseModel):
    """User submission to the contest."""
    team1: str
    team2: str
    score1: int = Field(ge=0, le=5)
    score2: int = Field(ge=0, le=5)
    points_earned: int = Field(ge=0)

    def to_leaderboard_entry(self, user: str = "You (Demo)") -> LeaderboardEntry:
        return LeaderboardEntry(
            user=user,
            points=self.points_earned,
            prediction=f"{self.team1} {self.score1}-{self.score2} {self.team2}",
        )