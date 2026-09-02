import logging
from typing import List, Optional

from first_aid_rag.config import settings
from first_aid_rag.interfaces.llm_interface import LLMProvider
from first_aid_rag.prompts.manager import PromptManager, detect_locale
from first_aid_rag.schemas.llm import ClinicalLLMResponse, GenerateResponse
from first_aid_rag.services.retrieval_service import RetrievalService
from first_aid_rag.stores.llm.factory import LLMFactory

logger = logging.getLogger(__name__)


class GenerationService:
    """End-to-End Clinical Generation Service with Score Threshold Filtering (Top 3 >= 80%) & Citation Tracking."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        llm_provider: Optional[LLMProvider] = None,
        prompt_manager: Optional[PromptManager] = None,
        min_score_threshold: float = settings.MIN_SIMILARITY_SCORE_THRESHOLD,
        arabic_min_score_threshold: float = settings.ARABIC_MIN_SIMILARITY_SCORE_THRESHOLD,
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.llm_provider = llm_provider or LLMFactory().create()
        self.prompt_manager = prompt_manager or PromptManager()
        self.min_score_threshold = min_score_threshold
        self.arabic_min_score_threshold = arabic_min_score_threshold

    async def generate_response(self, query: str) -> GenerateResponse:
        """Execute clinical RAG generation pipeline: Intent Check -> Retrieval -> Filter Top 3 (>=80% or >=75% for Arabic) -> LLM + Citations -> AND Gate."""
        clean_query = query.strip()
        logger.info("Starting Clinical Generation Pipeline for query: '%.60s...'", clean_query)

        # 0. Preliminary Fast Intent Check
        is_in_scope = await self.llm_provider.is_query_in_scope(clean_query)
        if not is_in_scope:
            logger.warning("Query rejected by preliminary scope check: '%.60s...'", clean_query)
            locale = detect_locale(clean_query)
            refusal_result = ClinicalLLMResponse(
                is_in_scope=False,
                is_knowledge_sufficient=True,
                answer=None,
                citations=[],
                refusal_reason=self.prompt_manager.get_out_of_scope_refusal(locale),
                provider="gemini",
                model_name=settings.GEMINI_MODEL,
                filtered_chunks_count=0,
            )
            return GenerateResponse(
                query=clean_query,
                result=refusal_result,
                retrieved_chunks_count=0,
                filtered_chunks_count=0,
            )

        # Determine language and effective similarity score threshold
        locale = detect_locale(clean_query)
        effective_threshold = (
            self.arabic_min_score_threshold if locale == "ar" else self.min_score_threshold
        )

        # 1. Retrieve candidates via Hybrid Vector Search + RRF Fusion
        retrieval_query = clean_query
        if locale == "ar":
            retrieval_query = await self.llm_provider.translate_to_english(clean_query)
            logger.info("Translated Arabic query to English for better Hybrid Search retrieval: '%s'", retrieval_query)
            
        retrieval_response = await self.retrieval_service.search(query=retrieval_query)
        raw_results = retrieval_response.results

        # 2. Filter retrieved candidates by similarity score threshold
        filtered_candidates: List[dict] = []
        for idx, item in enumerate(raw_results, 1):
            if item.percentage_score >= effective_threshold:
                raw_chunk_id = getattr(item, "chunk_id", None)
                if not raw_chunk_id or raw_chunk_id == item.document_id:
                    unique_chunk_id = f"chunk_p{item.pdf_page}_{idx}"
                else:
                    unique_chunk_id = str(raw_chunk_id)

                filtered_candidates.append({
                    "chunk_id": unique_chunk_id,
                    "document_id": item.document_id,
                    "source": item.source,
                    "text": item.text,
                    "score": item.score,
                    "percentage_score": item.percentage_score,
                    "pdf_page": item.pdf_page,
                    "section": item.section,
                    "recommendation_id": item.recommendation_id,
                    "is_table": item.is_table,
                })

        retrieved_count = len(raw_results)
        total_filtered_count = len(filtered_candidates)

        # Select ONLY top 3 candidates matching threshold
        top_3_candidates = filtered_candidates[:3]
        selected_count = len(top_3_candidates)

        logger.info(
            "Retrieval Stats: %d total retrieved | %d passed >= %.0f%% threshold (locale: %s) | %d top chunks passed to LLM.",
            retrieved_count, total_filtered_count, effective_threshold, locale, selected_count,
        )

        # 3. Guardrail Layer 1: If 0 candidates pass threshold, skip LLM call entirely
        if selected_count == 0:
            logger.warning("0 chunks passed %.0f%% threshold. Refusing generation without calling LLM.", effective_threshold)
            refusal_result = ClinicalLLMResponse(
                is_in_scope=True,
                is_knowledge_sufficient=False,
                answer=None,
                citations=[],
                refusal_reason=self.prompt_manager.get_insufficient_evidence_refusal(
                    detect_locale(clean_query)
                ),
                provider="gemini",
                model_name=settings.GEMINI_MODEL,
                filtered_chunks_count=0,
            )
            return GenerateResponse(
                query=clean_query,
                result=refusal_result,
                retrieved_chunks_count=retrieved_count,
                filtered_chunks_count=0,
            )

        # 4. Invoke LLM Provider with top 3 filtered chunks
        llm_response = await self.llm_provider.generate(
            query=clean_query,
            filtered_docs=top_3_candidates,
        )

        # 5. Guardrail Layer 2: Local AND-Gate verification
        if not (llm_response.is_in_scope and llm_response.is_knowledge_sufficient):
            logger.info("AND-Gate Refusal triggered by LLM evaluation.")
            llm_response.answer = None
            llm_response.citations = []
            
            locale = detect_locale(clean_query)
            if not llm_response.is_in_scope:
                llm_response.refusal_reason = self.prompt_manager.get_out_of_scope_refusal(locale)
            else:
                llm_response.refusal_reason = self.prompt_manager.get_insufficient_evidence_refusal(locale)

        return GenerateResponse(
            query=clean_query,
            result=llm_response,
            retrieved_chunks_count=retrieved_count,
            filtered_chunks_count=selected_count,
        )
