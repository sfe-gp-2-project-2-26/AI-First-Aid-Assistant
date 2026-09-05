import logging
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from first_aid_rag.config import settings
from first_aid_rag.routes.generation import router as generation_router
from first_aid_rag.routes.ingestion import router as ingestion_router
from first_aid_rag.routes.retrieval import router as retrieval_router
from first_aid_rag.routes.transcription import router as transcription_router

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="First Aid RAG API - Ingestion, Hybrid Retrieval & Clinical Generation",
    version="2.0.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router)
app.include_router(retrieval_router)
app.include_router(generation_router)
app.include_router(transcription_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "embedding_provider": settings.EMBEDDING_PROVIDER_TYPE,
        "stt_provider": settings.STT_PROVIDER_TYPE,
        "qdrant_url": settings.QDRANT_URL,
    }


if __name__ == "__main__":
    uvicorn.run("first_aid_rag.main:app", host="0.0.0.0", port=3000, reload=True)
