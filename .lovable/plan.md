# Plan: Run backend locally, test the full system from the Lovable preview

## How it will work

```text
Lovable preview (UI)
   │  proxies via BACKEND_URL
   ▼
ngrok tunnel  →  your local backend (port 8000)
   │
   ├── /embed + /chunk_pdf  →  Colab ngrok URL (EMBEDDING_URL in .env)
   ├── /transcribe          →  Groq whisper-large-v3 (GROQ_API_KEY in .env)
   └── vectors              →  Qdrant (docker compose)
```

## Steps for you (local machine)

1. Download the project (ZIP from Lovable, or git clone of the connected repo).
2. In `backend/`, copy `.env.example` to `.env` and set:
   - `EMBEDDING_URL=https://scrawny-quotable-deceiver.ngrok-free.dev` (your Colab service)
   - `GROQ_API_KEY=<your key>`
   - `AMBULANCE_NUMBER=<local emergency number>`
   - Qdrant URL as in `.env.example`
3. Start everything with `docker compose up -d` (Qdrant + backend), or run the backend directly with `uv run uvicorn ...` if you prefer.
4. Expose the backend: `ngrok http 8000` → copy the https URL.
5. Upload your first-aid PDFs through the UI "Add document" button (or POST to `/api/v1/ingestion/upload`) so Qdrant has data.

## Steps for me (Lovable side)

1. Add the `BACKEND_URL` secret/env var on the Lovable project pointing to your backend ngrok URL so the preview proxies (`/api/backend/chat`, `/api/backend/transcribe`, `/api/backend/ingest`) reach your local machine. The UI already reads this — no code change needed.
2. Note: ngrok free URLs change on restart — when yours changes, just tell me the new URL and I update the env var.

## Verification (I run these once your ngrok URL is set)

1. `GET /health` through the tunnel → backend healthy.
2. Send a chat question from the Lovable preview → answer streams back (proves RAG + Colab embed + Qdrant chain).
3. Record a short audio in the UI → transcription text appears in the input (proves Groq STT path).
4. Upload a small PDF via "Add document" → response shows chunk/vector counts, then ask a question answerable from it.
5. Open the Hospitals page → map with nearest 5 medical places renders.

## Technical details

- No code changes expected; only the `BACKEND_URL` env var on Lovable and your local `.env`.
- The UI proxy routes already send the `ngrok-skip-browser-warning` header, so ngrok's interstitial page won't break requests.
- CORS is already enabled on the FastAPI app (`allow_origins=["*"]`).
