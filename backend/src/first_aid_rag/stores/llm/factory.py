import logging
from typing import Optional

from first_aid_rag.interfaces.llm_interface import LLMProvider
from first_aid_rag.models.enums import LLMProviderType

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory creating the configured LLMProvider implementation."""

    def create(self, provider_type: Optional[str] = None) -> LLMProvider:
        kind = provider_type or LLMProviderType.GEMINI.value

        if kind == LLMProviderType.GEMINI.value:
            from first_aid_rag.stores.llm.providers.gemini_llm import GeminiLLMProvider

            logger.info("LLMFactory: using Gemini LLM provider.")
            return GeminiLLMProvider()

        raise ValueError(f"Unsupported LLM provider type: {kind!r}")
