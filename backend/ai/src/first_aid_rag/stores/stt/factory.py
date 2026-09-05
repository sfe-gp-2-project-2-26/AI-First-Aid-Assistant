import logging
from typing import Optional

from first_aid_rag.config import settings
from first_aid_rag.interfaces.stt_interface import STTProvider
from first_aid_rag.models.enums import STTProviderType

logger = logging.getLogger(__name__)


class STTFactory:
    """Factory creating the configured STTProvider implementation."""

    def create(self, provider_type: Optional[str] = None) -> STTProvider:
        kind = provider_type or settings.STT_PROVIDER_TYPE

        if kind == STTProviderType.GROQ.value:
            from first_aid_rag.stores.stt.providers.groq_stt import GroqSTTProvider

            logger.info("STTFactory: using Groq STT provider (%s).", settings.GROQ_STT_MODEL)
            return GroqSTTProvider()

        raise ValueError(f"Unsupported STT provider type: {kind!r}")
