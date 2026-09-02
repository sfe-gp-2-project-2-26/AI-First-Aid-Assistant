import logging
from typing import Optional

from first_aid_rag.config import settings
from first_aid_rag.interfaces.embedding_interface import EmbeddingProvider
from first_aid_rag.models.enums import EmbeddingProviderType

logger = logging.getLogger(__name__)


class EmbeddingFactory:
    """Factory creating the configured EmbeddingProvider implementation."""

    def create(self, provider_type: Optional[str] = None) -> EmbeddingProvider:
        kind = provider_type or settings.EMBEDDING_PROVIDER_TYPE

        if kind == EmbeddingProviderType.REMOTE.value:
            if not settings.EMBEDDING_URL:
                raise ValueError(
                    "EMBEDDING_URL must be set when EMBEDDING_PROVIDER_TYPE=remote."
                )
            from first_aid_rag.stores.embedding.providers.remote_embedding import (
                RemoteEmbeddingProvider,
            )

            logger.info("EmbeddingFactory: using remote embedding provider (%s)", settings.EMBEDDING_URL)
            return RemoteEmbeddingProvider()

        raise ValueError(f"Unsupported embedding provider type: {kind!r}")
