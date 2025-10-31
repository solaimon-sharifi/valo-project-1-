# Valorant Spectator Ghost — Functional MVP

**What it does:** Accepts round stats and returns coaching tips + a loadout recommendation.

## Run locally
```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.app:app --reload
