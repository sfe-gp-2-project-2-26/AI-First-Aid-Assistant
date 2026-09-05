import pytest
from fastapi.testclient import TestClient
from first_aid_rag.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["ok", "healthy"]

def test_docs_endpoint():
    response = client.get("/docs")
    assert response.status_code == 200

def test_generate_endpoint_empty_query():
    response = client.post("/api/v1/generation/generate", json={"query": ""})
    # Pydantic validation (min_length=2) returns 422
    assert response.status_code == 422

def test_search_endpoint_empty_query():
    response = client.post("/api/v1/retrieval/search", json={"query": ""})
    assert response.status_code == 422

def test_hospitals_endpoint_structure():
    response = client.post("/api/v1/hospitals/nearest", json={"latitude": 30.0, "longitude": 31.0})
    # Since it tries to call real external Nominatim if not mocked in integration test,
    # it might return 200 or 503 depending on network. Let's just assert it's one of them.
    assert response.status_code in [200, 503]
