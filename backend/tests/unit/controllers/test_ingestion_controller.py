import pytest
from fastapi import UploadFile, HTTPException
from unittest.mock import AsyncMock, Mock
from io import BytesIO
from first_aid_rag.controllers.ingestion_controller import IngestionController

@pytest.mark.asyncio
async def test_non_pdf_file_raises_400():
    controller = IngestionController(document_service=AsyncMock())
    file = UploadFile(filename="test.txt", file=BytesIO(b"content"))
    
    with pytest.raises(HTTPException) as exc:
        await controller.handle_pdf_upload(file)
    assert exc.value.status_code == 400
    assert "PDF" in exc.value.detail

@pytest.mark.asyncio
async def test_empty_file_raises_400():
    controller = IngestionController(document_service=AsyncMock())
    file = UploadFile(filename="test.pdf", file=BytesIO(b""))
    
    with pytest.raises(HTTPException) as exc:
        await controller.handle_pdf_upload(file)
    assert exc.value.status_code == 400
    assert "empty" in exc.value.detail.lower()

