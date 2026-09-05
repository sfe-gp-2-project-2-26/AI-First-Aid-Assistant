import pytest
import httpx
from unittest.mock import patch, AsyncMock
from first_aid_rag.stores.embedding.providers.remote_embedding import RemoteEmbeddingProvider

@pytest.mark.asyncio
async def test_get_headers_no_api_key():
    provider = RemoteEmbeddingProvider(api_url="http://test", api_key="")
    headers = provider._get_headers()
    assert "Authorization" not in headers

@pytest.mark.asyncio
async def test_get_headers_with_api_key():
    provider = RemoteEmbeddingProvider(api_url="http://test", api_key="secret")
    headers = provider._get_headers()
    assert headers["Authorization"] == "Bearer secret"

@pytest.mark.asyncio
async def test_embed_documents_empty_list():
    provider = RemoteEmbeddingProvider(api_url="http://test")
    res = await provider.embed_documents([])
    assert res == []

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_embed_documents_success(mock_post):
    from unittest.mock import Mock
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "dense_size": 1024,
        "dense": [[0.1] * 1024],
        "sparse": [{"indices": [1, 2], "values": [0.5, 0.6]}]
    }
    mock_post.return_value = mock_resp
    
    provider = RemoteEmbeddingProvider(api_url="http://test", expected_dimension=1024)
    res = await provider.embed_documents(["test"])
    
    assert len(res) == 1
    assert len(res[0].dense) == 1024
    assert res[0].sparse_indices == [1, 2]

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_embed_documents_dimension_mismatch(mock_post):
    from unittest.mock import Mock
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "dense_size": 512,  # Expected 1024
        "dense": [[0.1] * 512],
        "sparse": [{"indices": [], "values": []}]
    }
    mock_post.return_value = mock_resp
    
    provider = RemoteEmbeddingProvider(api_url="http://test", expected_dimension=1024)
    with pytest.raises(RuntimeError) as exc:
        await provider.embed_documents(["test"])
    assert "Embedding API unavailable or failed" in str(exc.value)

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_embed_documents_http_error(mock_post):
    from unittest.mock import Mock
    mock_resp = Mock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"
    
    # We must patch HTTPStatusError explicitly if we want to mock properly,
    # or just let it return 500 and the provider will raise HTTPStatusError
    mock_post.return_value = mock_resp
    
    provider = RemoteEmbeddingProvider(api_url="http://test")
    with pytest.raises(RuntimeError):
        await provider.embed_documents(["test"])
