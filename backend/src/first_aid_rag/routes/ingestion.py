import logging
from fastapi import APIRouter, UploadFile, File, Depends
from first_aid_rag.controllers.ingestion_controller import IngestionController
from first_aid_rag.services.document_service import DocumentService
from first_aid_rag.stores.document_parser.factory import DocumentParserFactory
from first_aid_rag.stores.embedding.factory import EmbeddingFactory
from first_aid_rag.stores.vector_db.factory import VectorDBFactory
from first_aid_rag.schemas.ingestion import IngestionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ingestion", tags=["Ingestion Pipeline"])


def get_ingestion_controller() -> IngestionController:
    """Dependency provider building the IngestionController via factories (DIP)."""
    embedding_provider = EmbeddingFactory().create()
    parser = DocumentParserFactory().create()
    vector_store = VectorDBFactory().create()

    document_service = DocumentService(
        vector_store=vector_store,
        parser=parser,
        embedding_provider=embedding_provider,
    )
    return IngestionController(document_service=document_service)


@router.post(
    "/upload",
    response_model=IngestionResponse,
    summary="Upload and ingest a clinical PDF document",
    description="Parses PDF via Docling, cleans page furniture, performs structure-aware chunking with BAAI/bge-m3 tokenizer, extracts metadata, generates dense+sparse embeddings locally or via remote, and stores points in Qdrant.",
)
@router.post(
    "/ingest-pdf",
    response_model=IngestionResponse,
    include_in_schema=False,
)
async def upload_clinical_pdf(
    file: UploadFile = File(...),
    controller: IngestionController = Depends(get_ingestion_controller),
) -> IngestionResponse:
    return await controller.handle_pdf_upload(file)
