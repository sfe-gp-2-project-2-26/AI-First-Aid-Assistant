import logging
from typing import Optional
from first_aid_rag.interfaces.document_parser_interface import DocumentParser
from first_aid_rag.interfaces.embedding_interface import EmbeddingProvider
from first_aid_rag.interfaces.vdb_interface import VectorStore
from first_aid_rag.services.storage_service import StorageService
from first_aid_rag.stores.document_parser import PDFChunkingPipeline
from first_aid_rag.schemas.ingestion import IngestionResponse
from first_aid_rag.config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """High-Level Document Pipeline Service orchestrating document ingestion end-to-end."""

    def __init__(
        self,
        vector_store: VectorStore,
        parser: Optional[DocumentParser] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
        storage_service: Optional[StorageService] = None,
        pdf_pipeline: Optional[PDFChunkingPipeline] = None,
    ):
        self.parser = parser
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.storage_service = storage_service or StorageService()
        self.pdf_pipeline = pdf_pipeline or PDFChunkingPipeline()

    async def process_pdf(self, file_name: str, content: bytes) -> IngestionResponse:
        """Run full PDF ingestion pipeline using remote fallback."""
        # Step 1: Save file to src/assets/{file_hash}.pdf and check deduplication
        file_hash, file_path, file_exists = self.storage_service.save_file(content)

        from first_aid_rag.models.enums import IngestionStatus
        # Check if already ingested in Vector Store and exists on disk
        if file_exists and self.vector_store.document_exists(file_hash):
            logger.info(f"Document {file_name} (hash: {file_hash}) already ingested. Returning early response.")
            return IngestionResponse(
                status=IngestionStatus.ALREADY_EXISTS.value,
                document_id=file_hash,
                filename=file_name,
                chunks_created=0,
                vectors_stored=0,
                message="Document already ingested in assets storage and vector store.",
            )

        # If file was deleted from assets on disk, purge any old vectors from Vector Store before re-ingestion
        if self.vector_store.document_exists(file_hash):
            logger.info(f"Document {file_name} (hash: {file_hash}) was removed from assets on disk. Purging old vector points before re-ingestion.")
            self.vector_store.delete_document(file_hash)

        # Step 2: Run PDF Chunking & Embedding Pipeline (Remote)
        logger.info(
            f"Running PDF chunking & embedding pipeline for: {file_name} (ID: {file_hash}) "
            f"[Mode: {settings.DOCLING_PROVIDER_TYPE}/{settings.EMBEDDING_PROVIDER_TYPE}]"
        )
        
        chunks = await self.pdf_pipeline.process_pdf(
            pdf_path=file_path,
            embedding_provider=self.embedding_provider,
        )

        if not chunks:
            raise ValueError(f"No structural chunks returned from PDF chunking pipeline for '{file_name}'.")

        # Step 3: Upsert resulting DocumentChunk objects directly into Vector DB
        logger.info(f"Upserting {len(chunks)} DocumentChunk points into Vector DB...")
        stored_count = self.vector_store.upsert_document_chunks(chunks)

        return IngestionResponse(
            status=IngestionStatus.SUCCESS.value,
            document_id=file_hash,
            filename=file_name,
            chunks_created=len(chunks),
            vectors_stored=stored_count,
            message="PDF ingestion pipeline completed successfully.",
        )
