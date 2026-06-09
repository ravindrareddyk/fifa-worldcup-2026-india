# Changelog

All notable changes to the WC India Hub 2026 project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Structured logging with `logging` module across app and utils (replaced bare excepts).
- Pydantic v2 models for data validation (`ContestSubmission`, `LeaderboardEntry`, `PredictionResult`, `Match`).
- Robust SQLite persistence for contest leaderboard and subscribers (replaced fragile CSV).
- Centralized configuration via `pydantic-settings` (`.env` support, contest tuning, API keys).
- Expanded test suite with monetization, validation, and config tests + coverage in CI.
- MIT LICENSE file, CHANGELOG.md, and CONTRIBUTING.md.
- `.streamlit/config.toml` for professional theming and server settings.
- Professional export features (CSV downloads for leaderboard and schedule).
- Improved ML model metadata display and simple versioning.
- Enhanced CI with security scanning (pip-audit) and better test reporting.
- Rewards shop, cross-tab ML prediction import, editable affiliate links, personal stats in Monetize tab.
- SQLite-backed contest data with proper schema and reset support.

### Changed
- Monetization persistence refactored to SQLite for better robustness and transactions.
- Error handling improved with structured logs everywhere.
- Config now drives leaderboard size, points, and log level.
- Tests now cover Pydantic models and config.

### Fixed
- Typo in persist function name (`montization` → `monetization`).
- Better handling of missing data and API failures with logging.

## [0.2.0] - 2026-06 (Phase 2 Monetization)

### Added
- Full-featured 💰 Support & Monetize tab with:
  - Community Prediction Contest + leaderboard (points, gamification).
  - Rewards redemption system.
  - Newsletter / lead capture with persistence.
  - Integration with ML Predictions tab.
- CSV persistence for demo data (later replaced).
- Cross-feature state sharing.

## [0.1.0] - Initial Professional Release

### Added
- Core Streamlit app with 6 tabs (Schedule, Live Scores, ML Predictions, Monetize, Analytics, Teaching).
- RandomForest ML model with feature importance.
- Simulated live scores with graceful real-API stub.
- IST time conversion.
- Docker (non-root) + GitHub Actions (lint, train ML, build+push to GHCR).
- Basic tests and utils package separation.
- Professional README with badges, architecture notes, and teaching focus.
