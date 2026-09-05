import logging
from typing import Dict, List, Optional

from first_aid_rag.config import settings
from first_aid_rag.interfaces.embedding_interface import EmbeddingProvider
from first_aid_rag.interfaces.vdb_interface import VectorStore
from first_aid_rag.schemas.retrieval import RankedDocument, SearchResponse, SearchResult
from first_aid_rag.stores.embedding.factory import EmbeddingFactory
from first_aid_rag.stores.vector_db.factory import VectorDBFactory

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service orchestrating dense+sparse query embedding, Qdrant search, and RRF fusion.

    No reranker stage: the fused RRF ranking is the final ordering.
    """

    def __init__(
        self,
        embedding_provider: Optional[EmbeddingProvider] = None,
        vector_store: Optional[VectorStore] = None,
    ):
        self.embedding_provider = embedding_provider or EmbeddingFactory().create()
        self.vector_store = vector_store or VectorDBFactory().create()

    def reciprocal_rank_fusion(
        self,
        dense_hits: List[dict],
        sparse_hits: List[dict],
        k: int = settings.RRF_K,
        top_k: int = settings.HYBRID_TOP_K,
    ) -> List[RankedDocument]:
        """Combine dense and sparse candidate search results using Reciprocal Rank Fusion (RRF)."""
        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, dict] = {}

        def process_hits(hits: List[dict]):
            for rank_idx, hit in enumerate(hits):
                payload = hit.get("payload", {})
                chunk_id = payload.get("chunk_id") or hit.get("id")
                if not chunk_id:
                    continue

                rank = rank_idx + 1
                score_contrib = 1.0 / (k + rank)

                if chunk_id not in rrf_scores:
                    rrf_scores[chunk_id] = 0.0
                    doc_map[chunk_id] = {
                        "chunk_id": chunk_id,
                        "text": payload.get("text", ""),
                        "metadata": payload,
                    }
                rrf_scores[chunk_id] += score_contrib

        process_hits(dense_hits)
        process_hits(sparse_hits)

        fused_docs: List[RankedDocument] = []
        for chunk_id, score in rrf_scores.items():
            info = doc_map[chunk_id]
            fused_docs.append(
                RankedDocument(
                    chunk_id=chunk_id,
                    text=info["text"],
                    score=score,
                    metadata=info["metadata"],
                )
            )

        fused_docs.sort(key=lambda d: d.score, reverse=True)
        logger.info(
            "RRF Fusion completed: merged %d dense + %d sparse hits into %d unique docs (top %d retained).",
            len(dense_hits), len(sparse_hits), len(fused_docs), top_k,
        )
        return fused_docs[:top_k]

    async def search(
        self,
        query: str,
        dense_top_k: int = settings.DENSE_TOP_K,
        sparse_top_k: int = settings.SPARSE_TOP_K,
        hybrid_top_k: int = settings.HYBRID_TOP_K,
    ) -> SearchResponse:
        """Execute end-to-end retrieval flow: embed -> hybrid search -> RRF fusion."""
        from first_aid_rag.prompts import detect_locale


        clean_query = query.strip()
        logger.info("Retrieval started for query (length: %d chars)", len(clean_query))

        # 1. Embed query (dense + sparse)
        query_embedding = await self.embedding_provider.embed_query(clean_query)

        query_locale = detect_locale(clean_query)
        # The corpus is predominantly English. Lexical sparse tokens won't overlap for Arabic queries.
        if query_locale == "ar":
            logger.info("Arabic query detected against English corpus. Skipping sparse lexical search.")
            sparse_indices = []
            sparse_values = []
        else:
            sparse_indices = query_embedding.sparse_indices
            sparse_values = query_embedding.sparse_values
        sparse_indices = query_embedding.sparse_indices
        sparse_values = query_embedding.sparse_values

        # 2. Hybrid vector search in Qdrant
        dense_hits, sparse_hits = self.vector_store.hybrid_search(
            dense_vector=query_embedding.dense,
            sparse_indices=sparse_indices,
            sparse_values=sparse_values,
            dense_top_k=dense_top_k,
            sparse_top_k=sparse_top_k,
        )
        logger.info(
            "Qdrant retrieval completed: %d dense candidates, %d sparse candidates.",
            len(dense_hits), len(sparse_hits),
        )

        # 3. RRF Fusion — final ranking (no reranker)
        final_docs = self.reciprocal_rank_fusion(
            dense_hits=dense_hits,
            sparse_hits=sparse_hits,
            k=settings.RRF_K,
            top_k=hybrid_top_k,
        )
        logger.info("Retrieval complete: returning top %d results.", len(final_docs))

        # 4. Map to response schema with score normalization
        max_rrf_score = 2.0 / (settings.RRF_K + 1)
        search_results: List[SearchResult] = []
        for doc in final_docs:
            meta = doc.metadata
            norm_score = min(1.0, doc.score / max_rrf_score)
            pct_score = round(norm_score * 100.0, 2)

            pdf_pages_list = meta.get("pdf_pages") or []
            actual_page = meta.get("pdf_page")
            if (actual_page is None or actual_page == 1) and isinstance(pdf_pages_list, list) and len(pdf_pages_list) > 0:
                actual_page = pdf_pages_list[0]
            if actual_page is None:
                actual_page = 1

            search_results.append(
                SearchResult(
                    text=doc.text,
                    score=round(norm_score, 4),
                    percentage_score=pct_score,
                    document_id=meta.get("document_id", ""),
                    source=meta.get("source", ""),
                    pdf_page=int(actual_page),
                    document_page=int(actual_page),
                    section=meta.get("section", ""),
                    recommendation_id=meta.get("recommendation_id"),
                    is_table=meta.get("is_table", False),
                    evidence_level=meta.get("evidence_level"),
                    recommendation_class=meta.get("recommendation_class"),
                )
            )

        return SearchResponse(query=clean_query, results=search_results)
