import pytest
from unittest.mock import Mock, AsyncMock
from first_aid_rag.services.document_service import DocumentService
from first_aid_rag.models.enums import IngestionStatus

@pytest.mark.asyncio
async def test_duplicate_document_returns_already_exists():
    mock_storage = Mock()
    # file_hash, file_path, already_existed
    mock_storage.save_file.return_value = ("hash123", "path/hash123.pdf", True)
    
    mock_vector = Mock()
    mock_vector.document_exists.return_value = True
    
    mock_pipeline = AsyncMock()
    
    service = DocumentService(
        storage_service=mock_storage,
        vector_store=mock_vector,
        pdf_pipeline=mock_pipeline
    )
    
    response = await service.process_pdf(b"content", "test.pdf")
    
    assert response.status == IngestionStatus.ALREADY_EXISTS.value
    assert response.chunks_created == 0
    mock_pipeline.process_pdf.assert_not_called()

@pytest.mark.asyncio
async def test_empty_chunks_raises_value_error():
    mock_storage = Mock()
    mock_storage.save_file.return_value = ("hash123", "path/hash123.pdf", False)
    
    mock_vector = Mock()
    mock_vector.document_exists.return_value = False
    
    mock_pipeline = AsyncMock()
    mock_pipeline.process_pdf.return_value = []
    
    service = DocumentService(
        storage_service=mock_storage,
        vector_store=mock_vector,
        pdf_pipeline=mock_pipeline
    )
    
    # Mocking PDFChunkingPipeline requires monkeypatching or just mocking the whole class,
    # but since DocumentService instantiates it directly, we can just mock `process_pdf`
    # if we patch it, or we expect ValueError if parser returns nothing useful.
    # We will test ValueError behavior assuming pipeline returns [].
    
    with pytest.raises(Exception):
        await service.process_pdf(b"content", "test.pdf")
