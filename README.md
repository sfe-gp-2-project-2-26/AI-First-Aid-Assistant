# Clinical AI Assistant

An intelligent First Aid and Emergency Clinical Decision Support System based on Retrieval-Augmented Generation (RAG). The system processes verified medical guidelines, extracts clinical knowledge using hybrid dense-sparse vector indexing with reciprocal rank fusion (RRF), and delivers strictly bounded, actionable first aid guidance in Arabic and English.

## System Architecture Overview

The application is structured into three decoupled components:
- Frontend (`frontend/`): React application with TypeScript, Vite, Tailwind CSS, and shadcn/ui.
- Backend (`backend/`): Production-ready FastAPI service following Clean Architecture (Routes, Controllers, Services, Stores, and Interfaces) with automated unit and integration tests.
- Remote Microservice: GPU-accelerated microservice hosting the embedding and document parsing models.

## Prerequisites & Required API Keys

You only need to have the following:
1. Docker Desktop: Required to run the Qdrant vector database or full containerized deployment. Ensure Docker Desktop is open and running.
2. Active API Credentials:
   - Google Gemini API Key (for clinical LLM generation).
   - Groq API Key (for speech-to-text Whisper audio transcription).
3. The Remote Colab Microservice running.

## Required Pre-run Step: Colab Microservice

The embedding generation (BGE-M3 dense and sparse) and PDF layout parsing/chunking run on an external GPU microservice.

Run the following Google Colab notebook before starting the backend:
[Notebook Link](https://colab.research.google.com/drive/1deZ1D9VzyDvB2_xQ_Lq7152VD9TcWq0T?usp=sharing)

After running all cells in the notebook, copy the generated public URL (e.g., your ngrok tunnel URL) and save it for the `EMBEDDING_URL` variable.

## Environment Configuration

Create the backend environment file from the provided example:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and insert your API keys and the Colab URL:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
EMBEDDING_URL=https://your-colab-ngrok-url.ngrok-free.app
QDRANT_URL=http://localhost:6333
```

## Running the Application

Make sure Docker Desktop is running, then execute from the repository root:

```bash
docker compose up --build
```

Services will be available at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:3000
- Qdrant Vector Store: http://localhost:6333
- Interactive API Documentation: http://localhost:3000/docs

## Running Tests

Run the full automated test suite using `uv`:

```bash
cd backend
uv run pytest tests/unit tests/integration/test_api_routes.py -v
```
