import logging

from fastapi import APIRouter, Depends, status

from first_aid_rag.controllers.retrieval_controller import RetrievalController
from first_aid_rag.schemas.retrieval import SearchRequest, SearchResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/retrieval", tags=["Retrieval"])


def get_retrieval_controller() -> RetrievalController:
    return RetrievalController()


@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute hybrid search (dense + sparse) with RRF fusion.",
)
async def search_clinical_documents(
    request: SearchRequest,
    controller: RetrievalController = Depends(get_retrieval_controller),
) -> SearchResponse:
    """Perform hybrid retrieval on ingested clinical documents, returning ranked results with metadata provenance."""
    return await controller.search(request)
