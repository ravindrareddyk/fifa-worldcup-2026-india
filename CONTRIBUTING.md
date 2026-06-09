# Contributing to WC India Hub 2026

Thank you for your interest in contributing! This project is intentionally designed as a **teaching and portfolio reference** for Indian IT students and faculty. Contributions that improve robustness, teach best practices, or add clear educational value are highly welcome.

## Code of Conduct
Be respectful. This is an educational project used by students and faculty. All interactions should support learning.

## How to Contribute

### 1. Reporting Bugs or Suggesting Features
- Use GitHub Issues.
- For bugs: include steps to reproduce, expected vs actual behavior, environment (Python version, OS).
- For features: explain the teaching or professional value.

### 2. Development Setup
```bash
git clone https://github.com/ravindrareddyk/fifa-worldcup-2026-india.git
cd fifa-worldcup-2026-india
python -m venv .venv
source .venv/bin/activate   # or .\.venv\Scripts\activate on Windows
pip install -r requirements.txt
streamlit run wc_india_hub.py
```

Run tests:
```bash
pytest --cov=utils --cov-report=term-missing
```

### 3. Code Style
- Follow existing structure: keep UI logic in `wc_india_hub.py`, business logic in `utils/`.
- Use type hints.
- Add logging (via the existing structured logger) for important events and errors.
- Add or update tests for new logic.
- Run `ruff check .` and `black .` before committing.

### 4. Pull Requests
- Create a feature branch from `main`.
- Keep PRs focused (one feature or fix).
- Update `CHANGELOG.md` under the Unreleased section.
- Include a short description of educational value if applicable.
- Link related issues.

### 5. Areas We Especially Welcome
- Better error handling and observability.
- Expanded tests and CI improvements.
- Making the ML or monetization features more production-like (without overcomplicating for teaching).
- Documentation and teaching material in `docs/`.
- Accessibility or internationalization improvements.

## License
By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for helping make this a great learning resource!
