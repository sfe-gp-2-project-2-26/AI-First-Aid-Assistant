import pytest
from pydantic import ValidationError
from first_aid_rag.schemas.common import BaseQueryRequest
from first_aid_rag.schemas.retrieval import SearchRequest
from first_aid_rag.schemas.llm import GenerateRequest

def test_base_query_min_length():
    with pytest.raises(ValidationError):
        BaseQueryRequest(query="a")

def test_base_query_valid():
    req = BaseQueryRequest(query="test query")
    assert req.query == "test query"

def test_search_request_inherits_base():
    req = SearchRequest(query="test search")
    assert isinstance(req, BaseQueryRequest)

def test_generate_request_inherits_base():
    req = GenerateRequest(query="test generate")
    assert isinstance(req, BaseQueryRequest)

