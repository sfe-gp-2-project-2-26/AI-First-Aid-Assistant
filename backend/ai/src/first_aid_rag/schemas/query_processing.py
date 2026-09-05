from typing import Optional
from pydantic import BaseModel, Field
from first_aid_rag.models.enums.first_aid_topics import FirstAidTopic


class ProcessedQuery(BaseModel):
    """Output of the Query Processing stage."""
    
    original_query: str = Field(..., description="The raw user input.")
    processed_query: str = Field(..., description="English, retrieval-optimized query for embedding.")
    locale: str = Field(..., description="Detected locale: 'en' or 'ar'.")
    is_in_scope: bool = Field(..., description="Whether the query falls within First Aid scope.")
    topic_category: FirstAidTopic = Field(..., description="Best-matching topic from the First Aid document.")
    refusal_reason: Optional[str] = Field(default=None, description="Populated if is_in_scope=False.")

