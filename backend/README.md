# First Aid RAG — Backend Service

FastAPI backend built using Clean Architecture principles: abstract interfaces, store factories, MVC controllers, application services, Pydantic schemas, and centralized localized prompt management.

## Directory Structure

```text
src/first_aid_rag/
├── main.py                  # FastAPI application entry point
├── config.py                # Environment configuration using pydantic-settings
├── interfaces/              # Abstract contracts (Embedding, LLM, VectorStore, Parser, STT)
├── models/                  # Domain models and enums (provider types, ingestion status)
├── stores/                  # Store factories and provider implementations
│   ├── embedding/           # Remote GPU embedding provider (BGE-M3 dense and sparse)
│   ├── llm/                 # Gemini clinical provider
│   ├── vector_db/           # Qdrant vector database provider
│   ├── document_parser/     # Document parsing factory and PDF chunking pipeline
│   └── stt/                 # Groq Whisper STT provider
├── services/                # Business logic (retrieval, generation, document ingestion, hospitals)
├── controllers/             # Request orchestration and HTTP mapping
├── routes/                  # FastAPI routers and endpoint declarations
├── schemas/                 # Pydantic request and response schemas
└── prompts/                 # Prompt manager and localized clinical prompts (ar/en)
```

## Running Locally

### Prerequisites

You only need:
1. Docker Desktop: Required for the local Qdrant vector database.
2. The remote Colab GPU microservice running:
   https://colab.research.google.com/drive/1deZ1D9VzyDvB2_xQ_Lq7152VD9TcWq0T?usp=sharing
3. Active Gemini and Groq API keys.

You do not need to install Python manually; `uv` will download and configure Python 3.12 automatically.

### Setup and Execution

1. Start Qdrant in Docker:
```bash
docker run -d -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
```

2. Configure environment:
```bash
cp .env.example .env
```
Fill in `GEMINI_API_KEY`, `GROQ_API_KEY`, and `EMBEDDING_URL` (from your Colab ngrok tunnel).

3. Set up Python runtime and install dependencies with uv:
```bash
uv python install 3.12
uv venv --python 3.12
```

Activate the virtual environment:
- On Windows: `.venv\Scripts\activate`
- On Linux/macOS: `source .venv/bin/activate`

Install all dependencies:
```bash
uv pip install -e .
```

4. Run the API server:
```bash
uv run uvicorn first_aid_rag.main:app --host 0.0.0.0 --port 3000 --reload
```

## Automated Testing

Run the comprehensive unit test suite:

```bash
uv run pytest tests/unit -v
```

Run the full test suite including API integration routes:

```bash
uv run pytest tests/unit tests/integration/test_api_routes.py -v
```

## Main API Endpoints

- `GET  /health` — Service health check and configuration status
- `POST /api/v1/ingestion/upload` — Ingest and index a clinical PDF guideline
- `POST /api/v1/retrieval/search` — Hybrid dense and sparse vector search with RRF fusion
- `POST /api/v1/generation/generate` — End-to-end clinical RAG generation with citations
- `POST /api/v1/hospitals/nearest` — Find nearest medical facilities using geolocation
- `POST /transcribe` — Audio speech-to-text transcription via Groq Whisper
