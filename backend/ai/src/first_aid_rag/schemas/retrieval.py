from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from first_aid_rag.schemas.common import BaseQueryRequest


class RankedDocument(BaseModel):
    """Internal candidate representation passed through RRF fusion."""

    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseQueryRequest):
    """Retrieval search endpoint request payload."""
    pass


class SearchResult(BaseModel):
    """Individual search result item returned to API clients with full provenance."""

    text: str
    score: float
    percentage_score: float
    document_id: str
    source: str
    pdf_page: int
    document_page: int
    section: Optional[str] = ""
    recommendation_id: Optional[str] = None
    is_table: bool = False
    evidence_level: Optional[str] = None
    recommendation_class: Optional[str] = None



class SearchResponse(BaseModel):
    """Retrieval search response payload."""

    query: str
    results: List[SearchResult]

