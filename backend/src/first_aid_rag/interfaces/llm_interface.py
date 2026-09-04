from abc import ABC, abstractmethod
from typing import List, Optional
from first_aid_rag.schemas.llm import ClinicalLLMResponse
from first_aid_rag.schemas.query_processing import ProcessedQuery


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
    async def process_query(self, query: str) -> ProcessedQuery:
        """Process the query: detect locale, check scope, translate, rewrite, and classify topic."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check the operational status/connectivity of the LLM service."""
        pass
