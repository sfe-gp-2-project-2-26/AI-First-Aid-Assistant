from abc import ABC, abstractmethod
from typing import List, Tuple
from first_aid_rag.schemas.documents import DocumentChunk, EmbeddingResult


class VectorStore(ABC):
    """Abstract Interface for Vector Database operations."""

    @abstractmethod
    def ensure_collection(self) -> None:
        """Ensure the target collection exists with appropriate named dense and sparse vector configurations."""
        pass

    @abstractmethod
    def upsert_document_chunks(self, chunks: List[DocumentChunk]) -> int:
        """Upsert document chunks and their corresponding embeddings into the collection.
        Returns the count of vectors stored.
        """
        pass

    @abstractmethod
    def document_exists(self, document_id: str) -> bool:
        """Check if any points belonging to document_id already exist in the vector store."""
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        """Delete all points associated with a document_id from the vector store."""
        pass

    @abstractmethod
    def hybrid_search(
        self,
        dense_vector: List[float],
        sparse_indices: List[int],
        sparse_values: List[float],
        dense_top_k: int,
        sparse_top_k: int,
    ) -> Tuple[List[dict], List[dict]]:
        """Perform separate dense and sparse search against named vectors.
        Returns a tuple of (dense_hits, sparse_hits), where each hit is a dict containing
        payload fields and raw similarity score.
        """
        pass

