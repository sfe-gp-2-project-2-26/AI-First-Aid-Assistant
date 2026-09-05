import pytest
from unittest.mock import patch, MagicMock
from first_aid_rag.stores.vector_db.providers.qdrant import QdrantProvider
from first_aid_rag.schemas.documents import DocumentChunk, ChunkMetadata

@pytest.fixture
def mock_qdrant_client():
    with patch("first_aid_rag.stores.vector_db.providers.qdrant.QdrantClient") as mock:
        yield mock.return_value

def test_upsert_empty_chunks_returns_zero(mock_qdrant_client):
    provider = QdrantProvider(url="http://test")
    provider._client = mock_qdrant_client
    
    assert provider.upsert_document_chunks([]) == 0

def test_document_exists_true(mock_qdrant_client):
    # Mocking scroll to return some results
    mock_qdrant_client.scroll.return_value = ([MagicMock()], None)
    
    provider = QdrantProvider(url="http://test")
    provider._client = mock_qdrant_client
    
    assert provider.document_exists("doc_1") is True

def test_document_exists_false(mock_qdrant_client):
    # Mocking scroll to return empty list
    mock_qdrant_client.scroll.return_value = ([], None)
    
    provider = QdrantProvider(url="http://test")
    provider._client = mock_qdrant_client
    
    assert provider.document_exists("doc_2") is False

def test_hybrid_search_no_sparse_skips_sparse(mock_qdrant_client):
    provider = QdrantProvider(url="http://test")
    provider._client = mock_qdrant_client
    
    # Mock the internal search method
    with patch.object(provider, '_search_named_vector') as mock_search:
        mock_search.return_value = [{"id": "hit1"}]
        
        dense, sparse = provider.hybrid_search(
            dense_vector=[0.1, 0.2],
            sparse_indices=[],
            sparse_values=[]
        )
        
        assert len(dense) == 1
        assert len(sparse) == 0
        # It should only have been called once for dense
        mock_search.assert_called_once()
        assert mock_search.call_args[0][0] == "dense"

