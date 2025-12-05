# Frontend - React + Vite

This SPA is built with Vite and shipped via nginx in production; the UI fetches `/models`, `/health`, and `/process-pdf`.

### Install

```bash
cd frontend
npm install
```

### Run locally

`npm run dev` starts the Vite dev server on port 5173. It proxies `/process-pdf`, `/health`, and `/models` to `http://127.0.0.1:8000`, so keep the backend running locally.

### Build & Docker

```bash
npm run build
```

- The build outputs to `dist/`. The Dockerfile copies the compile output into nginx and configures proxies to the backend.
- For a complete stack you can run `docker compose up --build frontend` from the repo root, which will also pick up `backend` (and Grobid) thanks to the shared compose file.

### Environment

Ensure the root `.env` (see `.env.example`) contains `GEMINI_API_KEY`; the frontend relies on the backend to validate that API key before calling Gemini.
