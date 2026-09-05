import pytest
from first_aid_rag.services.retrieval_service import RetrievalService

def test_rrf_empty_lists():
    service = RetrievalService(embedding_provider=None, vector_store=None)
    results = service.reciprocal_rank_fusion(dense_hits=[], sparse_hits=[])
    assert len(results) == 0

def test_rrf_only_dense():
    service = RetrievalService(embedding_provider=None, vector_store=None)
    dense = [
        {"id": "doc1", "payload": {"chunk_id": "doc1", "text": "A"}},
        {"id": "doc2", "payload": {"chunk_id": "doc2", "text": "B"}},
    ]
    results = service.reciprocal_rank_fusion(dense_hits=dense, sparse_hits=[])
    assert len(results) == 2
    assert results[0].chunk_id == "doc1"
    assert results[1].chunk_id == "doc2"
    assert results[0].score > results[1].score

def test_rrf_combined_boosts_common_doc():
    service = RetrievalService(embedding_provider=None, vector_store=None)
    dense = [
        {"id": "doc1", "payload": {"chunk_id": "doc1", "text": "A"}},
        {"id": "doc2", "payload": {"chunk_id": "doc2", "text": "B"}},
    ]
    sparse = [
        {"id": "doc3", "payload": {"chunk_id": "doc3", "text": "C"}},
        {"id": "doc2", "payload": {"chunk_id": "doc2", "text": "B"}},
    ]
    results = service.reciprocal_rank_fusion(dense_hits=dense, sparse_hits=sparse)
    
    # doc2 is in both, so it should get a score boost
    # dense: doc1(rank1), doc2(rank2)
    # sparse: doc3(rank1), doc2(rank2)
    # RRF(doc2) = 1/(k+2) + 1/(k+2) = 2/(k+2)
    # RRF(doc1) = 1/(k+1)
    # For k=60, RRF(doc2) = 2/62 = 0.0322
    # For k=60, RRF(doc1) = 1/61 = 0.0163
    # Therefore doc2 should be ranked 1st
    assert results[0].chunk_id == "doc2"

def test_rrf_top_k_limits_results():
    service = RetrievalService(embedding_provider=None, vector_store=None)
    dense = [{"id": f"doc{i}", "payload": {"chunk_id": f"doc{i}", "text": f"Text {i}"}} for i in range(10)]
    results = service.reciprocal_rank_fusion(dense_hits=dense, sparse_hits=[], top_k=3)
    assert len(results) == 3

