import logging
from typing import Optional

from first_aid_rag.interfaces.vdb_interface import VectorStore
from first_aid_rag.models.enums import VectorDBProviderType

logger = logging.getLogger(__name__)


class VectorDBFactory:
    """Factory creating the configured VectorStore implementation."""

    def create(self, provider_type: Optional[str] = None) -> VectorStore:
        kind = provider_type or VectorDBProviderType.QDRANT.value

        if kind == VectorDBProviderType.QDRANT.value:
            from first_aid_rag.stores.vector_db.providers.qdrant import QdrantProvider

            logger.info("VectorDBFactory: using Qdrant vector store.")
            return QdrantProvider()

        raise ValueError(f"Unsupported vector DB provider type: {kind!r}")
