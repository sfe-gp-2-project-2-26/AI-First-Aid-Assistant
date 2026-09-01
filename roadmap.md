# Roadmap

- [x] Port frontend from Clinical_Hackathon `src/UI` into this project (builds clean)
- [x] Generalize backend proxy (`/api/backend/generate`) with `BACKEND_URL` env default
- [x] Responsive pass + mobile-only "Call Ambulance" button (`VITE_AMBULANCE_NUMBER`)
- [x] Voice input: mic button, MediaRecorder, POST to `/transcribe` via proxy
- [x] Hospitals map page `/hospitals` (Leaflet + Overpass + OSRM, green=nearest)
- [x] Backend restructure to boilerplate layout in `backend/` (`src/first_aid_rag`, factories, prompt manager, remote embedding, STT/Groq)
- [x] uv migration (pyproject.toml), backend Dockerfile, frontend Dockerfile, docker-compose.yml, .env.example, README
- [x] Remote-only embedding + PDF chunking (`{EMBEDDING_URL}/embed`, `{EMBEDDING_URL}/chunk_pdf`); torch/transformers made optional
- [x] PDF upload from the UI -> `/api/backend/ingest` -> backend ingestion -> remote parse+embed -> Qdrant
