# Frontend - React + Vite

### Install

```bash
cd frontend
npm install
```

### Run locally

`npm run dev` starts Vite on port 5173 and proxies `/api` to `http://127.0.0.1:8000` so the React client talks to the FastAPI backend without CORS headaches.

### Build

`npm run build` compiles the static assets into `dist/` for deployment.
