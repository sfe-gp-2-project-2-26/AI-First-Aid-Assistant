from first_aid_rag.schemas.documents import ChunkMetadata, DocumentChunk, EmbeddingResult, ParsedDocument
import pytest
from pydantic import ValidationError

def test_chunk_metadata_defaults():
    meta = ChunkMetadata(chunk_id="test_1", document_id="doc_1")
    assert meta.language == "en"
    assert meta.source_type == "clinical_guideline"
    assert meta.content_type == "text"
    assert meta.pdf_page == 1

def test_chunk_metadata_required_fields():
    with pytest.raises(ValidationError):
        ChunkMetadata()

def test_document_chunk_creation(sample_chunk_metadata):
    chunk = DocumentChunk(
        chunk_id="test_1",
        text="text",
        metadata=sample_chunk_metadata
    )
    assert chunk.dense_vector is None
    assert chunk.sparse_indices is None

def test_embedding_result_creation():
    result = EmbeddingResult(
        dense=[0.1, 0.2],
        sparse_indices=[1],
        sparse_values=[0.5]
    )
    assert len(result.dense) == 2
    assert result.sparse_indices == [1]

def test_parsed_document_empty_sections():
    doc = ParsedDocument(
        document_id="doc_1",
        title="Title",
        total_pages=1
    )
    assert doc.sections == []

