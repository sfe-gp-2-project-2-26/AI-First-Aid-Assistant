# Clinical First-Aid RAG — Refactor + Features (Revised Scope)

## Deliverable
A full project you download and run on your machine with `docker compose up -d`, containing:
- A Python RAG backend restructured to the `RAG-Boilerplate` conventions
- A responsive TanStack Start frontend in a `views/` folder (MVC view layer)
- Call Ambulance button (mobile only)
- Nearest-hospitals map page

While building here, the frontend will point at your ngrok backend
`https://undercook-cogwheel-undone.ngrok-free.dev` so the full system can be tested in the Lovable preview.

## Scope changes from the previous plan
Removed for this stage: PostgreSQL, the Node.js service, login/registration, first-visit cookies, and server-side chat history. Qdrant remains the only datastore. The `memory` interface and factory are still scaffolded in the backend (the boilerplate mandates them) but wired to an in-memory provider only.

## Constraint
The Lovable preview runs the frontend only. The Python service runs on your machine; the preview reaches it through your ngrok URL. Backend code is delivered as files in the repo, verified by reading and by live calls against your ngrok endpoint.

---

## Part 1 — Backend restructure (Python / AI)

Package directory `src/first_aid_rag/` (importable name; `pyproject.toml` distribution name `first-aid-rag`, since Python packages cannot contain hyphens).

```text
src/first_aid_rag/
├── main.py              # FastAPI app factory, CORS, router registration, /health
├── config.py            # pydantic-settings, replaces config/settings.py
├── routes/              # ingestion, retrieval, generation, transcribe, health
├── controllers/         # existing controllers, framework-agnostic
├── schemas/routes/      # existing Pydantic DTOs
├── models/enums/        # ProviderType, LanguageCode, MessageRole
├── interfaces/          # llm, embedding, vdb, memory, parser, stt
├── stores/
│   ├── llm/{factory.py,providers/}          # gemini
│   ├── embedding/{factory.py,providers/}    # remote (default), local
│   ├── vector_db/{factory.py,providers/}    # qdrant
│   ├── memory/{factory.py,providers/}       # in-memory
│   └── stt/{factory.py,providers/}          # groq (whisper-large-v3)
├── prompts/manager.py + templates/locales/{ar,en}/
├── utils/               # logging, error handlers, clinical_regex
└── assets/
```

Work items:
- Create the package root; move existing modules into their layer; convert imports to package-absolute (`from first_aid_rag.config import settings`).
- Add the five factories the boilerplate mandates. Each resolves a provider name from config and returns an interface implementation, so controllers depend only on abstractions.
- Add `PromptManager` with `ar`/`en` templates, extracting prompt strings currently inlined in the generation controller.
- Add an `STTFactory` + `interfaces/stt.py` with a Groq provider calling `whisper-large-v3` (audio file in, transcript text out, configurable model name). The `POST /transcribe` route accepts `multipart/form-data` with field `file`, validates it is a non-empty audio upload, forwards it to the provider, and returns `{ "text": "..." }` — the exact contract the frontend voice input expects.
- Keep controllers free of FastAPI types; routes own status codes and validation.
- Move `src/tests/` to top-level `tests/`; delete `src/scratch/`.

MVC mapping: `routes` = transport edge, `controllers` + `services` = application logic, `models`/`schemas` = model layer, `views/` = view layer.

### Embedding provider — remote by default
`EmbeddingFactory` resolves on `EMBEDDING_PROVIDER_TYPE`:
- `remote` (default) — posts to `EMBEDDING_URL` (your Colab/ngrok endpoint doing parsing + embedding). Sends the `ngrok-skip-browser-warning` header, has a configurable timeout, and raises a typed error the route maps to a clear HTTP status.
- `local` — the existing in-process BAAI/bge-m3 provider, kept behind the same interface.

`.env.example` will carry `EMBEDDING_PROVIDER_TYPE=remote`, `EMBEDDING_URL=`, `QDRANT_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `GROQ_API_KEY` (for the `/transcribe` route), `GROQ_STT_MODEL=whisper-large-v3`, `AMBULANCE_NUMBER`, `VITE_BACKEND_URL`, and `VITE_API_BASE_URL` (for the transcription endpoint). Note: since the backend runs on your machine, `GROQ_API_KEY` goes in your local `.env` — the copy stored in Lovable is only for testing the full system from the preview.

## Part 2 — Remove Streamlit
Delete `app.py`, drop the `streamlit-ui` compose service, and remove `streamlit` from dependencies. The `views/` app becomes the only frontend.

## Part 3 — uv instead of pip
Replace `requirements.txt` with `pyproject.toml` (`requires-python >=3.12`, `uv_build` backend). With `remote` as the default embedding provider, the heavy ML stack (torch, FlagEmbedding, transformers, docling) moves to an optional `[project.optional-dependencies] local` extra, so the default `uv sync` is small and fast. Commit `uv.lock`. Dockerfile becomes a multi-stage `uv sync --frozen` build.

## Part 4 — Frontend (`views/`)

The current `src/UI` app is ported into this Lovable project and will ship in the repo as `views/`.

- **Responsive** — mobile-first pass over every screen: sidebar becomes a drawer on small screens, fluid chat column, touch-sized targets, safe-area insets, no horizontal overflow.
- **Call Ambulance button** — pinned at the top of the chat page, rendered only on mobile. Detection uses a coarse-pointer / no-hover media query combined with viewport width (not user-agent sniffing, so it stays correct on resize). Renders `<a href="tel:...">` with the number from `AMBULANCE_NUMBER`, exposed to the browser as a build-time `VITE_AMBULANCE_NUMBER`.
- **Voice input** — a microphone button next to the chat text input. First click starts `MediaRecorder` recording with a clear active state (pulsing indicator + elapsed timer); second click stops, packages the audio as a `webm`/`wav` file, and POSTs it as `multipart/form-data` (field name `file`) to `{VITE_API_BASE_URL}/transcribe` (the backend route from Part 1, backed by Groq `whisper-large-v3`). A loading state shows while waiting; the returned `{ "text": "..." }` populates the existing input for review and editing — it never auto-submits. Microphone-permission denial, recording errors, and request failures each surface a clear inline message instead of crashing.
- **Hospitals page** (`/hospitals`) — new route. Requests geolocation, queries Overpass API for the 5 nearest hospitals/medical facilities, then OSRM for a route to each. Leaflet renders the nearest route as a green polyline and the other four in red, with distance (km) and ETA labels on each route, plus a ranked list beside the map. Graceful fallbacks when permission is denied or no results are found. Leaflet is dynamically imported behind a client-only boundary since it touches `window` at import time.
- **Backend wiring** — the existing `/api/backend/generate` proxy is generalised into a small server-route layer that forwards to `VITE_BACKEND_URL` (defaulting to your ngrok URL in the preview, `http://backend:3000` in compose), preserving the `ngrok-skip-browser-warning` header and the current upstream-error handling.
- **Chat history** — deferred with the rest of the removed scope. Messages persist for the active session only.
- **Head metadata** — distinct title/description/OG tags per route.

## Part 5 — One-command startup

`docker compose up -d` starts three services:
- `qdrant` — vector store, persistent volume
- `backend` — FastAPI on port 3000, `uv`-based image, healthcheck on `/health`
- `views` — the TanStack Start app on port 8080, depends on backend health

A single root `.env.example` documents every variable.

---

## Order of work
1. Port the frontend into this Lovable project and get it building.
2. Point it at your ngrok backend and confirm the chat round-trip works live.
3. Responsive pass + Call Ambulance button.
4. Hospitals map page.
5. Backend restructure into the boilerplate layout, factories, prompt manager, remote embedding provider.
6. `uv` migration, Dockerfile, docker compose, `.env.example`, README.
