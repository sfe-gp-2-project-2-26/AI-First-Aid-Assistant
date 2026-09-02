from abc import ABC, abstractmethod
from typing import List, Optional
from first_aid_rag.schemas.llm import ClinicalLLMResponse


class LLMProvider(ABC):
    """Abstract Interface for Clinical LLM Providers."""

    @abstractmethod
    async def generate(
        self,
        query: str,
        filtered_docs: List[dict],
        system_prompt: Optional[str] = None
    ) -> ClinicalLLMResponse:
        """Generate structured clinical response adhering to Diabetes scope and context sufficiency rules."""
        pass

    @abstractmethod
    async def is_query_in_scope(self, query: str) -> bool:
        """Fast preliminary check to see if the query is in the scope of first aid/emergencies."""
        pass

    @abstractmethod
    async def translate_to_english(self, text: str) -> str:
        """Translate the given text to English."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check the operational status/connectivity of the LLM service."""
        pass
