import pytest
from unittest.mock import patch, AsyncMock
import httpx
from first_aid_rag.services.pdf_chunking_pipeline import PDFChunkingPipeline

def test_derive_content_role_caution():
    pipeline = PDFChunkingPipeline()
    assert pipeline._derive_content_role(["Warning: High risk"]) == "caution"

def test_derive_content_role_first_aid():
    pipeline = PDFChunkingPipeline()
    assert pipeline._derive_content_role(["Chapter 1", "First Aid Steps"]) == "first_aid_steps"

def test_derive_content_role_none():
    pipeline = PDFChunkingPipeline()
    assert pipeline._derive_content_role(["Introduction"]) == "introduction"
    assert pipeline._derive_content_role(["Just some text"]) is None

def test_map_content_type_table():
    pipeline = PDFChunkingPipeline()
    assert pipeline._map_content_type(["table"]) == "table"

def test_map_content_type_figure():
    pipeline = PDFChunkingPipeline()
    assert pipeline._map_content_type(["picture"]) == "figure"
    assert pipeline._map_content_type(["caption"]) == "figure"

def test_map_content_type_text_default():
    pipeline = PDFChunkingPipeline()
    assert pipeline._map_content_type([]) == "text"

def test_calculate_token_count():
    pipeline = PDFChunkingPipeline()
    assert pipeline._calculate_token_count("one two three") == 3

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_process_pdf_success(mock_post, tmp_path):
    # Mocking two sequential post calls (chunk_pdf and embed)
    # This is slightly complex in AsyncMock, so we define a side_effect function
    async def mock_post_side_effect(url, **kwargs):
        from unittest.mock import Mock
        resp = Mock()
        resp.status_code = 200
        if "chunk_pdf" in url:
            resp.json.return_value = {
                "total_pages": 1,
                "chunk_count": 1,
                "chunks": [
                    {
                        "chunk_index": 0,
                        "text": "Hello world",
                        "contextualized_text": "Header - Hello world",
                        "headings": ["Header"],
                        "pages": [1],
                        "doc_item_labels": ["text"]
                    }
                ]
            }
        elif "embed" in url:
            resp.json.return_value = {
                "dense": [[0.1] * 1024],
                "sparse": [{"indices": [1], "values": [0.5]}]
            }
        return resp

    mock_post.side_effect = mock_post_side_effect
    
    # Create dummy pdf
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"dummy pdf content")
    
    # Needs EMBEDDING_URL set in settings, we will assume it is or set it.
    from first_aid_rag.config import settings
    settings.EMBEDDING_URL = "http://test"
    
    pipeline = PDFChunkingPipeline()
    chunks = await pipeline.process_pdf(str(pdf_file))
    
    assert len(chunks) == 1
    assert chunks[0].text == "Hello world"
    assert chunks[0].metadata.chunk_index == 0
    assert chunks[0].metadata.section == "Header"
    assert len(chunks[0].dense_vector) == 1024
    assert chunks[0].sparse_indices == [1]

@pytest.mark.asyncio
async def test_process_pdf_no_url():
    from first_aid_rag.config import settings
    old_url = settings.EMBEDDING_URL
    settings.EMBEDDING_URL = ""
    
    pipeline = PDFChunkingPipeline()
    with pytest.raises(ValueError) as exc:
        await pipeline.process_pdf("dummy.pdf")
    
    assert "EMBEDDING_URL is not set" in str(exc.value)
    settings.EMBEDDING_URL = old_url
