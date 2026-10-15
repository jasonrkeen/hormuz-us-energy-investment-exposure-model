> This file mirrors `.github/copilot-instructions.md`; keep both in sync when either changes.

# CLAUDE.md — Hormuz U.S. Energy Investment Exposure Model

## Purpose
Investment-intelligence model evaluating Strait of Hormuz disruption, U.S. refining economics, valuation, and cycle-normalized prospective exposure.

## Tech stack
- Python; dependencies in `requirements.txt`
- Key libraries: `pandas`, `numpy`, `yfinance`

## Folder structure
- `charts/` (4 files)
- `data/` (6 files)
- `outputs/` (15 files)
- `research/` (8 files)
- `src/` (11 files)
- `tests/` (2 files)
- `README.md`
- `VERSION`
- `main.py`
- `requirements.txt`

## Setup, run, test
Commands documented in README.md (referenced files exist):
```bash
python -m venv .venv
pip install -r requirements.txt
python main.py
python -m unittest discover -s tests -v
```
- Tests: 2 Python test file(s) under `tests/`; framework appears to be unittest. Add/update tests with any logic change.

## Conventions observed
- Functions use type hints; keep annotating new code.
- Random seeds are set for reproducibility (Monte Carlo/simulation); keep seeded, deterministic runs.
- Public data sources referenced: EIA, SEC, yfinance.
- Write paths relative to the repo root (no absolute local paths).

## Output artifacts
- Generated outputs go to `outputs/`.

## Guardrails
- Never commit secrets, API keys, tokens, or `.env` files.
- Do not commit large raw datasets or binaries; keep data fetched or documented with its source.
- Keep analysis source-backed: cite data sources and assumptions; label scenario/forecast outputs as model estimates, not facts.
- Preserve reproducibility: no unseeded randomness, no hidden manual steps.
