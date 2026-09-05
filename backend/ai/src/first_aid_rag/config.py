"""Application configuration.

Type-safe settings via Pydantic BaseSettings. All values can be overridden
through environment variables or a .env file at the backend root.
"""

from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application Settings."""

    APP_NAME: str = "first-aid-rag"
    DEBUG: bool = True

    # Qdrant Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "clinical_documents"

    # Embedding Provider ("remote" = external HTTP API, e.g. Colab behind ngrok)
    EMBEDDING_PROVIDER_TYPE: str = "remote"  # "local" | "remote"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIMENSION: int = 1024
    EMBEDDING_DEVICE: str = "auto"  # "auto" | "cuda" | "cpu" (local provider only)
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_TIMEOUT: int = 30
    EMBEDDING_URL: str = ""  # Required when EMBEDDING_PROVIDER_TYPE="remote"
    EMBEDDING_API_KEY: str = ""

    # Document Parsing (Docling) — "remote" delegates /chunk_pdf to the Colab service
    DOCLING_PROVIDER_TYPE: str = "remote"  # "local" | "remote"
    DOCLING_DO_OCR: bool = False

    # Speech-to-Text (Groq Whisper)
    STT_PROVIDER_TYPE: str = "groq"
    GROQ_API_KEY: str = ""
    GROQ_STT_MODEL: str = "whisper-large-v3"
    STT_TIMEOUT: int = 60

    # Storage
    ASSETS_DIR: str = "assets"

    # Retrieval & Search
    DENSE_TOP_K: int = 20
    SPARSE_TOP_K: int = 20
    HYBRID_TOP_K: int = 20
    RRF_K: int = 60

    # Gemini LLM Provider
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    MIN_SIMILARITY_SCORE_THRESHOLD: float = 80.0
    ARABIC_MIN_SIMILARITY_SCORE_THRESHOLD: float = 75.0


    model_config = {
        "env_file": str(ENV_FILE_PATH) if ENV_FILE_PATH.exists() else ".env",
        "extra": "ignore",
    }


settings = Settings()
