from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RankedDocument(BaseModel):
    """Internal candidate representation passed through RRF fusion."""

    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    """Retrieval search endpoint request payload."""

    query: str = Field(..., min_length=1, description="Clinical query string")


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



class SearchResponse(BaseModel):
    """Retrieval search response payload."""

    query: str
    results: List[SearchResult]

