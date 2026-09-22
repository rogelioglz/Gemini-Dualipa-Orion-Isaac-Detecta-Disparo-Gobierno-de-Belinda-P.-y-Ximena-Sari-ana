# Gemini Mobile + PWA + Backend skeleton

This branch adds a minimal FastAPI backend and a React PWA frontend skeleton to let you submit sound detection JSON from a phone and generate reports (simulated by default).

Quickstart (local):

1) Backend

  cd backend
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  export API_KEY=dev-secret
  export SIMULATE_GEMINI=true
  uvicorn app.main:app --reload

2) Frontend

  cd web
  npm install
  npm run dev

Notes:
- The backend reads GEMINI_API_KEY and SIMULATE_GEMINI env vars. By default SIMULATE_GEMINI=true for development.
- Replace storage with S3 or database for production. Do not expose GEMINI_API_KEY in the frontend.
