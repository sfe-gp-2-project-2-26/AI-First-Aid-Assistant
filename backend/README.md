# First Aid RAG — Backend

FastAPI backend restructured after the RAG-Boilerplate layout: interfaces + factories, controllers, routes, services, schemas, and a central prompt manager.

## Layout

```text
src/first_aid_rag/
├── main.py                  # FastAPI entry point
├── config.py                # pydantic-settings (all env config)
├── interfaces/              # Abstract contracts (embedding, LLM, VDB, parser, STT)
├── models/enums/            # Provider type enums
├── stores/                  # Factories + provider implementations
│   ├── embedding/           # remote (ngrok/Colab) | local (BGE-M3)
│   ├── llm/                 # Gemini
│   ├── vector_db/           # Qdrant
│   ├── document_parser/     # remote | local Docling
│   └── stt/                 # Groq whisper-large-v3
├── services/                # Business logic (retrieval, generation, document, ...)
├── controllers/             # Request orchestration (MVC controllers)
├── routes/                  # FastAPI routers
├── schemas/                 # Pydantic request/response models
└── prompts/                 # Prompt manager + en/ar locales
```

## Run locally (uv)

```bash
cp .env.example .env   # fill in GEMINI_API_KEY, GROQ_API_KEY, EMBEDDING_URL
uv venv && source .venv/bin/activate
uv pip install -e .
uv run uvicorn first_aid_rag.main:app --host 0.0.0.0 --port 3000 --reload
```

For local (in-process) embedding/parsing instead of the remote ngrok service:

```bash
uv pip install -e ".[local]"
# then set EMBEDDING_PROVIDER_TYPE=local and DOCLING_PROVIDER_TYPE=local in .env
```

## Endpoints

- `GET  /health`
- `POST /api/v1/ingestion/upload` — ingest a clinical PDF
- `POST /api/v1/retrieval/search` — hybrid dense+sparse search with RRF fusion
- `POST /api/v1/generation/generate` — end-to-end RAG answer with citations
- `POST /transcribe` — multipart `file` -> `{"text": "..."}` (Groq Whisper)
