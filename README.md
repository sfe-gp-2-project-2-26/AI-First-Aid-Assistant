# Clinical AI Assistant

An intelligent First Aid and Emergency Clinical Decision Support System based on Retrieval-Augmented Generation (RAG). The system processes verified medical guidelines, extracts clinical knowledge using hybrid dense-sparse vector indexing with reciprocal rank fusion (RRF), and delivers strictly bounded, actionable first aid guidance in Arabic and English.

## System Architecture Overview

The application is structured into a microservices architecture:

- **Frontend (`frontend/`)**: React application using TanStack Router, TypeScript, Vite, Tailwind CSS, and shadcn/ui. Acts as a BFF (Backend For Frontend) proxy to securely manage cookies and CORS.
- **Auth & Session Backend (`backend/auth/`)**: Node.js/Express service backed by MongoDB that handles JWT authentication, secure HttpOnly cookie issuance, user registration with strong password validation, and multi-session conversation history (renaming, deleting, loading past chats).
- **Core Clinical Backend (`backend/ai/`)**: Production-ready FastAPI Python service following Clean Architecture that handles RAG retrieval, Qdrant integration, LLM generation, and Audio transcription.
- **Remote Microservice**: GPU-accelerated microservice hosting the BGE-M3 embedding and document parsing models.

## Key Features

- **Hybrid RAG Search**: Dense and Sparse vector search utilizing Reciprocal Rank Fusion.
- **User Authentication**: JWT-based auth via HttpOnly cookies with strong password validation (Min 8 chars, uppercase, lowercase, numbers, symbols).
- **Persistent Chat Sessions**: Authenticated users have their conversation history saved in MongoDB. Includes ability to seamlessly switch between, rename, or delete past sessions via the sidebar.
- **Guest Mode**: Unauthenticated users can use the core assistant features without history persistence.
- **Voice Inputs**: Uses Groq Whisper API for rapid speech-to-text input.

## Prerequisites & Required API Keys

You only need to have the following:

1. **Docker Desktop**: Required to run the full containerized deployment (Qdrant, MongoDB, Frontend, Auth Node, FastAPI). Ensure Docker Desktop is open and running.
2. **Active API Credentials**:
   - Google Gemini API Key (for clinical LLM generation).
   - Groq API Key (for speech-to-text Whisper audio transcription).
3. **The Remote Colab Microservice running**.

## Required Pre-run Step: Colab Microservice

The embedding generation (BGE-M3 dense and sparse) and PDF layout parsing/chunking run on an external GPU microservice.

Run the following Google Colab notebook before starting the backend:
[Notebook Link](https://colab.research.google.com/drive/1deZ1D9VzyDvB2_xQ_Lq7152VD9TcWq0T?usp=sharing)

After running all cells in the notebook, copy the generated public URL (e.g., your ngrok tunnel URL) and save it for the `EMBEDDING_URL` variable.

## Environment Configuration

### 1. Root Environment (Frontend & Docker Compose)

Create the root environment file from the example:

```bash
cp .env.example .env
```

### 2. Backend Environment

Create the backend environment file from the provided example:

```bash
cd backend/ai
cp .env.example .env
```

Edit `backend/ai/.env` and insert your API keys and the Colab URL:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
EMBEDDING_URL=https://your-colab-ngrok-url.ngrok-free.app
QDRANT_URL=http://qdrant:6333
```

_(Note: The auth backend uses a default hardcoded `JWT_SECRET_KEY` inside `docker-compose.yml`, which can be overridden by an environment variable in production)._

## Running the Application

Make sure Docker Desktop is running, then execute from the repository root:

```bash
docker compose up --build
```

Services will be spun up and available at:

- **Frontend UI**: http://localhost:8080
- **Auth Node Backend**: http://localhost:4000
- **FastAPI Core Backend**: http://localhost:3000
- **MongoDB**: mongodb://localhost:27017
- **Qdrant Vector Store**: http://localhost:6333
- **Interactive API Documentation (FastAPI)**: http://localhost:3000/docs

## Running Tests

Run the full automated test suite for the core Python backend using `uv`:

```bash
cd backend/ai
uv run pytest tests/unit tests/integration/test_api_routes.py -v
```
