import logging
from typing import Optional

from fastapi import HTTPException, status

from first_aid_rag.schemas.retrieval import SearchRequest, SearchResponse
from first_aid_rag.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


class RetrievalController:
    """Controller handling retrieval search endpoints."""

    def __init__(self, retrieval_service: Optional[RetrievalService] = None):
        self.retrieval_service = retrieval_service or RetrievalService()

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Handle search request validation and invoke RetrievalService."""
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query string cannot be empty.",
            )

        try:
            return await self.retrieval_service.search(query=request.query)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error during clinical search retrieval: %s", e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Clinical retrieval failed: {str(e)}",
            )
