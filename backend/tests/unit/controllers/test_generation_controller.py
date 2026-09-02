import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock
from first_aid_rag.controllers.generation_controller import GenerationController
from first_aid_rag.schemas.llm import GenerateRequest

@pytest.mark.asyncio
async def test_empty_query_raises_400():
    controller = GenerationController(generation_service=AsyncMock())
    with pytest.raises(HTTPException) as exc:
        await controller.generate(GenerateRequest(query="   "))
    assert exc.value.status_code == 400
    assert "empty" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_service_exception_raises_500():
    mock_service = AsyncMock()
    mock_service.generate_response.side_effect = Exception("DB offline")
    controller = GenerationController(generation_service=mock_service)
    
    with pytest.raises(HTTPException) as exc:
        await controller.generate(GenerateRequest(query="test query"))
    assert exc.value.status_code == 500

