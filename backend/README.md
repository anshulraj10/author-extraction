# Backend - FastAPI

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Launch:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
3. Health endpoints are exposed under `/health` and `/extract`.

Extend `app/main.py` to plug in backend logic and persistence.
