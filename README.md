# Author Extraction

Monorepo skeleton for a FastAPI backend powering a React frontend. Designed for GitHub deployment.

## Structure

- `backend/` – FastAPI service with a stub author extraction endpoint.
- `frontend/` – React + Vite SPA that hits the backend API.

## Getting started

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Development flow

- Iterate on `backend/app/main.py` for API logic.
- Extend `frontend/src/App.tsx` to consume the API.

## Deploying on GitHub

- Push both `backend/` and `frontend/` directories.
- Add GitHub Actions workflows (not included yet) for lint/test/publish if needed.
