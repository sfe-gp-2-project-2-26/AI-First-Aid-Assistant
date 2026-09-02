from pydantic import BaseModel, Field

class BaseQueryRequest(BaseModel):
    """Base query request shared across retrieval and generation."""
    query: str = Field(..., min_length=2, description="Clinical query string.")

