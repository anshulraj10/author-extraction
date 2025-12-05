# Author Extraction

Monorepo for an author-extraction prototype: FastAPI handles PDF ingestion + metadata parsing while a React/Vite SPA consumes the API, renders author tables, and exports CSV/Excel. The repo ships docker files for each service plus a `docker-compose.yml` that also starts a Grobid container.

## Layout

- `backend/` – FastAPI server with Grobid/Gemini wiring.
- `frontend/` – React UI built with Vite and served through nginx (with proxies for `/process-pdf`, `/health`, `/models`).
- `docker-compose.yml` – grobid, backend, and frontend services.

## Environment

1. Copy `.env.example` to `.env` (root of the repo) and set `GEMINI_API_KEY` so the backend can talk to Gemini.
2. Grobid connection defaults to `http://grobid:8070` inside Docker; override `GROBID_CONFIG_PATH` if you need a custom file.

## Running with Docker Compose

```bash
docker compose up --build
```

- Grobid listens on `8070` (reused by the backend).
- Backend (FastAPI) exposes `http://localhost:8000`.
- Frontend (nginx + Vite build) is reachable at `http://localhost:5173`.

Use `docker compose logs -f backend` if the backend fails to process PDFs.

## Running locally (optional)

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Make sure `.env` with `GEMINI_API_KEY` is present before hitting `/process-pdf`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies `/process-pdf`, `/health`, and `/models` to `http://127.0.0.1:8000`.

## Development flow

- Update `backend/app/main.py` and related modules when changing the ingestion pipeline.
- Evolve `frontend/src/App.tsx` for richer UI, exports, and modal interactions.

## Deploying on GitHub

- Push backend and frontend directories plus the docker assets.
- Add workflows as needed for lint/test/build (not included yet).
