# 🏆 WC India Hub 2026

**FIFA World Cup 2026 Fan Dashboard for Indian Supporters**  
Live IST Schedule • ML-Powered Predictions • Simulated Live Scores • Built for Teaching + Portfolio

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white&style=for-the-badge)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white&style=for-the-badge)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white&style=for-the-badge)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white&style=for-the-badge)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white&style=for-the-badge)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

## ✨ Key Features

- **📅 Accurate IST Schedule** — All match times converted to Indian Standard Time using public openfootball data with robust fallback
- **🔴 Live Scores (Simulated)** — Beautiful demo mode with one-click goal simulation. Real football API integration stub ready (`FOOTBALL_API_KEY`)
- **🔮 ML Predictions** — Beginner-friendly **RandomForest** model that outputs win/draw probabilities + expected score. Feature importance explained in the UI.
- **📊 Rich Analytics** — Interactive Plotly charts for groups, team strength, distributions
- **🧑‍🏫 Teaching-First Design** — Clean `utils/` package, Pydantic models, structured logging, SQLite example, documented code, MLOps & DevOps patterns students can actually extend
- **🚀 Production-Grade DevOps** — Non-root Docker, healthchecks, GitHub Actions with GHCR publishing, model training in CI, security scanning, Dependabot
- **🛡️ Robustness** — Structured logging, Pydantic validation, SQLite persistence for contest data, centralized config with pydantic-settings, improved error handling
- **📤 Professional Features** — CSV exports for schedule & leaderboard, model versioning/metadata display, configurable affiliate links, full rewards/engagement system in monetization tab

---

## 📸 Screenshots

> **Add your own screenshots here after running the app!**

| Schedule + IST | Live Scores (Demo) | ML Predictions |
|----------------|--------------------|----------------|
| ![Schedule](docs/screenshots/schedule.png) | ![Live](docs/screenshots/live.png) | ![ML](docs/screenshots/ml.png) |

**How to generate screenshots:**
```bash
streamlit run wc_india_hub.py
# Take screenshots of each tab and save to docs/screenshots/
```

---

## 🚀 Quick Start

### 1. Local Development (Recommended)

```bash
git clone https://github.com/<your-org>/wc-india-hub-2026.git
cd wc-india-hub-2026

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

streamlit run wc_india_hub.py
```

Open http://localhost:8501

### 2. With Docker

```bash
docker build -t wc-india-hub:local .
docker run -p 8501:8501 wc-india-hub:local
```

### 3. Docker Compose (Best for Dev)

```bash
docker compose up --build
```

Copy `.env.example` → `.env` if you want to experiment with real APIs.

---

## 🧠 The ML Model (Beginner Level)

Located in `utils/ml_model.py`:

- Uses **RandomForestClassifier** (easy to explain)
- Features: team strength difference, knockout flag, neutral venue
- Trained on `data/historical_matches.csv` (synthetic + real patterns)
- Persisted with `joblib` to `data/wc2026_model.joblib`
- UI shows probabilities + **feature importance** for teaching

**Retrain manually:**
```bash
python -m utils.train_model
```

The same functions are used in both the Streamlit app and the Jupyter notebook (`notebooks/worldcup_ml_predictions.ipynb`).

**Student extension ideas:**
- Add real World Cup historical results (2014–2022)
- Move to 3-class classification (Win / Draw / Loss)
- Add probability calibration or simple betting odds simulation

---

## 🔴 Live Scores Architecture

The app demonstrates a **very common real-world pattern**:

1. **Default**: High-quality simulated data (`utils/live_scores.py`)
2. **Feature flag**: `use_real_api=True` + `FOOTBALL_API_KEY` environment variable
3. **Graceful degradation**: Falls back to simulation if the real API fails or key is missing

This is excellent for portfolios and teaching because it always looks good in demos.

---

## 🐳 DevOps & CI/CD (Showcase Quality)

### Dockerfile Highlights
- `python:3.11-slim`
- Non-root user (`appuser`)
- Proper layer caching
- Healthcheck
- OCI labels for image metadata

### GitHub Actions (`.github/workflows/deploy.yml`)
- **lint-and-test**: Ruff + Black + pytest
- **train-ml-model**: Actually trains the ML model in CI (MLOps!)
- **build-and-push**: Builds and pushes to **GitHub Container Registry (GHCR)** on main
- Caching, proper permissions, metadata

**Badges you can add after first successful run:**
```markdown
![CI](https://github.com/<org>/wc-india-hub-2026/actions/workflows/deploy.yml/badge.svg)
```

---

## 📁 Project Structure

```
wc-india-hub-2026/
├── wc_india_hub.py              # Main Streamlit application (UI only)
├── Dockerfile                   # Production-grade container
├── docker-compose.yml           # One-command local development
├── .dockerignore
├── requirements.txt
├── .env.example
├── README.md
│
├── .github/workflows/
│   └── deploy.yml               # Full CI/CD (lint → train → build → push to GHCR)
│
├── data/
│   ├── team_strength.csv        # Hand-curated team ratings (easy to extend)
│   ├── historical_matches.csv   # Training data for the ML model
│   ├── wc2026_model.joblib      # Persisted RandomForest (auto-generated)
│   └── .gitkeep
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py           # Fixtures + strength + historical (with caching)
│   ├── ml_model.py              # Train / load / predict logic (beginner friendly)
│   ├── live_scores.py           # Simulation + real API stub
│   ├── ist_utils.py             # All IST conversion logic
│   └── train_model.py           # Standalone training script (MLOps)
│
├── notebooks/
│   └── worldcup_ml_predictions.ipynb   # Educational notebook matching production code
│
├── tests/
│   └── test_basic.py            # Smoke tests (pytest)
│
└── docs/                        # Teaching materials & screenshots
```

---

## 🎓 Career Highlights & Teaching Value (For Faculty / Portfolio)

This project was deliberately built to demonstrate **multiple modern competencies** in one cohesive repository:

| Area              | What This Repo Shows                                      |
|-------------------|-----------------------------------------------------------|
| **Python**        | Clean package structure, type hints in spirit, error handling |
| **Data/ML**       | Real scikit-learn usage, feature engineering, model persistence, probability outputs |
| **MLOps**         | Model training in CI, artifact management, reproducible training script |
| **DevOps**        | Docker best practices (non-root, healthcheck, labels), multi-job GitHub Actions, GHCR |
| **Web Apps**      | Professional Streamlit patterns (session state, caching, tabs, metrics) |
| **API Integration** | Simulated vs real API pattern with environment configuration |
| **Teaching**      | Dedicated student tab, documented code, suggested exercises |

**Perfect for:**
- Faculty portfolios when applying for teaching positions
- Student final year / capstone projects
- Demonstrating "I can take an idea from notebook → production container → CI/CD"

---

## 🔧 Environment & Secrets

```bash
cp .env.example .env
# Edit .env and add FOOTBALL_API_KEY if you have one
```

For Streamlit Cloud, use **Secrets** (`.streamlit/secrets.toml`) instead of `.env`.

---

## 🛠️ Development Commands

```bash
# Lint
ruff check .

# Format
black .

# Test
pytest

# Retrain model
python -m utils.train_model

# Run app
streamlit run wc_india_hub.py
```

---

## 🚢 Deployment Options

- **GitHub Container Registry** — already wired via Actions
- **Streamlit Community Cloud** — free and excellent for this kind of app
- **Railway / Fly.io / Render** — great Docker support
- **Self-hosted** — `docker compose up`

---

## 📜 License

MIT License — free to use for education, portfolios, and personal projects.

---

## ❤️ Credits & Inspiration

- Fixture data: [openfootball/worldcup.json](https://github.com/openfootball/worldcup.json)
- Built with love for Indian football fans by IT Faculty
- Designed as a complete, honest, **teachable** full-stack Python project

---

**Share your deployments and improvements!**  
Tag `@wcindiahub2026` on LinkedIn / Instagram / X.

---

> _"The best portfolio projects are the ones you would actually want to maintain and extend."_
