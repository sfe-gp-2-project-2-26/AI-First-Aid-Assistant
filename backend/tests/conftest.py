import pytest
import os
import shutil
import tempfile
from unittest.mock import AsyncMock, Mock

from first_aid_rag.schemas.documents import ChunkMetadata, DocumentChunk, EmbeddingResult
from first_aid_rag.interfaces.embedding_interface import EmbeddingProvider
from first_aid_rag.interfaces.vdb_interface import VectorStore
from first_aid_rag.interfaces.llm_interface import LLMProvider


@pytest.fixture
def sample_chunk_metadata():
    return ChunkMetadata(
        chunk_id="test_chunk_1",
        document_id="test_doc_1",
        document_title="Test Document",
        source="test.pdf",
        content_type="text",
        pdf_pages=[1],
        pdf_page=1,
        heading_path=["Header 1"],
        section="Header 1",
        content_role="first_aid_steps",
        token_count=100,
        chunk_index=0,
        content_hash="hash123"
    )

@pytest.fixture
def sample_document_chunk(sample_chunk_metadata):
    return DocumentChunk(
        chunk_id="test_chunk_1",
        text="This is a test chunk.",
        metadata=sample_chunk_metadata,
        dense_vector=[0.1] * 1024,
        sparse_indices=[1, 2, 3],
        sparse_values=[0.5, 0.6, 0.7]
    )

@pytest.fixture
def sample_embedding_result():
    return EmbeddingResult(
        dense=[0.1] * 1024,
        sparse_indices=[1, 2, 3],
        sparse_values=[0.5, 0.6, 0.7]
    )

@pytest.fixture
def mock_embedding_provider():
    provider = AsyncMock(spec=EmbeddingProvider)
    return provider

@pytest.fixture
def mock_vector_store():
    store = Mock(spec=VectorStore)
    return store

@pytest.fixture
def mock_llm_provider():
    provider = AsyncMock(spec=LLMProvider)
    return provider

@pytest.fixture
def temp_assets_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

