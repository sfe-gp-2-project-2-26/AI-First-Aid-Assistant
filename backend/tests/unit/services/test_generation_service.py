import pytest
from unittest.mock import AsyncMock, Mock
from first_aid_rag.services.generation_service import GenerationService
from first_aid_rag.schemas.llm import ClinicalLLMResponse
from first_aid_rag.schemas.retrieval import SearchResponse, SearchResult

@pytest.mark.asyncio
async def test_out_of_scope_query_no_retrieval():
    mock_llm = AsyncMock()
    mock_llm.is_query_in_scope.return_value = False
    
    mock_retrieval = AsyncMock()
    
    service = GenerationService(
        retrieval_service=mock_retrieval,
        llm_provider=mock_llm,
    )
    
    response = await service.generate_response("What is the recipe for cake?")
    
    assert response.result.is_in_scope is False
    assert response.result.answer is None
    assert "scope" in response.result.refusal_reason.lower()
    
    # Should not retrieve or generate
    mock_retrieval.search.assert_not_called()
    mock_llm.generate.assert_not_called()

@pytest.mark.asyncio
async def test_zero_chunks_above_threshold_no_llm():
    mock_llm = AsyncMock()
    mock_llm.is_query_in_scope.return_value = True
    
    mock_retrieval = AsyncMock()
    # All chunks below 80%
    mock_retrieval.search.return_value = SearchResponse(
        query="CPR",
        results=[
            SearchResult(
                text="A", 
                score=0.5, 
                percentage_score=50.0, 
                document_id="1",
                source="test.pdf",
                pdf_page=1,
                document_page=1
            )
        ]
    )
    
    service = GenerationService(
        retrieval_service=mock_retrieval,
        llm_provider=mock_llm,
        min_score_threshold=80.0
    )
    
    response = await service.generate_response("How to do CPR?")
    
    assert response.filtered_chunks_count == 0
    assert response.result.is_knowledge_sufficient is False
    assert "insufficient" in response.result.refusal_reason.lower()
    mock_llm.generate.assert_not_called()

@pytest.mark.asyncio
async def test_successful_response_passes_and_gate():
    mock_llm = AsyncMock()
    mock_llm.is_query_in_scope.return_value = True
    mock_llm.generate.return_value = ClinicalLLMResponse(
        is_in_scope=True,
        is_knowledge_sufficient=True,
        answer="Do chest compressions.",
        citations=[],
        provider="gemini",
        model_name="gemini-1.5-flash",
        filtered_chunks_count=1
    )
    
    mock_retrieval = AsyncMock()
    mock_retrieval.search.return_value = SearchResponse(
        query="CPR",
        results=[
            SearchResult(
                text="A", 
                score=0.9, 
                percentage_score=90.0, 
                document_id="1",
                source="test.pdf",
                pdf_page=1,
                document_page=1
            )
        ]
    )
    
    service = GenerationService(
        retrieval_service=mock_retrieval,
        llm_provider=mock_llm,
        min_score_threshold=80.0
    )
    
    response = await service.generate_response("How to do CPR?")
    
    assert response.result.is_in_scope is True
    assert response.result.is_knowledge_sufficient is True
    assert response.result.answer == "Do chest compressions."
    assert response.result.refusal_reason is None

@pytest.mark.asyncio
async def test_arabic_query_passes_at_75_threshold():
    mock_llm = AsyncMock()
    mock_llm.is_query_in_scope.return_value = True
    mock_llm.translate_to_english.return_value = "How to do CPR?"
    mock_llm.generate.return_value = ClinicalLLMResponse(
        is_in_scope=True,
        is_knowledge_sufficient=True,
        answer="قم بالضغط على الصدر.",
        citations=[],
        provider="gemini",
        model_name="gemini-1.5-flash",
        filtered_chunks_count=1
    )
    
    mock_retrieval = AsyncMock()
    # Chunk with 76% score (would fail English 80% threshold, but passes Arabic 75% threshold)
    mock_retrieval.search.return_value = SearchResponse(
        query="كيف أقوم بالإنعاش القلبي؟",
        results=[
            SearchResult(
                text="CPR Instructions", 
                score=0.76, 
                percentage_score=76.0, 
                document_id="1",
                source="cpr.pdf",
                pdf_page=1,
                document_page=1
            )
        ]
    )
    
    service = GenerationService(
        retrieval_service=mock_retrieval,
        llm_provider=mock_llm,
        min_score_threshold=80.0,
        arabic_min_score_threshold=75.0,
    )
    
    response = await service.generate_response("كيف أقوم بالإنعاش القلبي؟")
    
    assert response.filtered_chunks_count == 1
    assert response.result.is_knowledge_sufficient is True
    assert response.result.answer == "قم بالضغط على الصدر."

