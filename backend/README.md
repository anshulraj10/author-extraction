# Backend - FastAPI

Read the repo-level `README.md` first for an overview, Docker workflows, and how the services link together.

## Environment

- Create a `.env` file in the repository root (copy `.env.example`) and set `GEMINI_API_KEY` so the backend can reach Google Gemini when processing references.
- The backend loads the Grobid configuration from `backend/app/grobid-config.json` (or `GROBID_CONFIG_PATH` if you override it).

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

- `/health` and `/models` expose metadata used by the frontend dropdown/modal.
- `/process-pdf` accepts a PDF form field (`file`) plus the `model_id` form value and returns cleaned JSON.

## Running inside Docker

Use the monorepo `docker compose up --build` to start Grobid, the backend, and nginx-backed frontend together.

```bash
docker compose up --build backend
```

- Backend logs (`docker compose logs -f backend`) will show Grobid/Gemini health checks and ingestion progress.
