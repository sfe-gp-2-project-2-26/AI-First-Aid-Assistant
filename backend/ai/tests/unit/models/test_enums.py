import pytest
from first_aid_rag.models.enums import IngestionStatus, EmbeddingProviderType, DocumentParserType, STTProviderType

def test_ingestion_status_values():
    assert IngestionStatus.SUCCESS.value == "success"
    assert IngestionStatus.ALREADY_EXISTS.value == "already_exists"
    assert IngestionStatus.ERROR.value == "error"

def test_embedding_provider_type_values():
    assert EmbeddingProviderType.LOCAL.value == "local"
    assert EmbeddingProviderType.REMOTE.value == "remote"

def test_document_parser_type_values():
    assert DocumentParserType.LOCAL.value == "local"
    assert DocumentParserType.REMOTE.value == "remote"

def test_enums_are_str_serializable():
    # Should work since they inherit from str, Enum
    assert isinstance(STTProviderType.GROQ, str)
    assert isinstance(IngestionStatus.SUCCESS, str)

