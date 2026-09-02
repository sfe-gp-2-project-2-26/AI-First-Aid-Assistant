import pytest
import asyncio
from pathlib import Path
from first_aid_rag.config import settings
from first_aid_rag.stores.embedding.providers.remote_embedding import RemoteEmbeddingProvider
from first_aid_rag.services.pdf_chunking_pipeline import PDFChunkingPipeline

# A very minimal, valid PDF file in bytes
MINIMAL_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Count 1\n/Kids [ 3 0 R ]\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [ 0 0 612 792 ]\n/Resources <<\n/Font << /F1 4 0 R >>\n>>\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000212 00000 n\n0000000295 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n386\n%%EOF\n"

@pytest.fixture(scope="module")
def ensure_remote_url():
    if not settings.EMBEDDING_URL:
        pytest.skip("EMBEDDING_URL is not set in environment. Skipping real remote integration tests.")

@pytest.mark.asyncio
async def test_real_remote_embedding(ensure_remote_url):
    """
    Real HTTP Request to the Remote Embedding Service.
    WARNING: Requires the actual Colab endpoint to be running!
    """
    provider = RemoteEmbeddingProvider(
        api_url=settings.EMBEDDING_URL,
        timeout=180.0
    )
    
    # Send a tiny batch to the real server
    texts = ["This is a real integration test for medical RAG.", "CPR is important."]
    
    results = await provider.embed_documents(texts)
    
    assert len(results) == 2, "Remote API did not return 2 results."
    assert results[0].dense is not None, "No dense vector returned."
    
    # Allow either 1024 (bge-m3) or 768 or any actual size configured on the server
    assert len(results[0].dense) > 0, "Dense vector is empty."
    
    # Depending on model, sparse might be populated
    if results[0].sparse_indices is not None:
        assert len(results[0].sparse_indices) == len(results[0].sparse_values)

@pytest.mark.asyncio
async def test_real_remote_pdf_chunking(ensure_remote_url, tmp_path):
    """
    Real HTTP Request to the Remote PDF Chunking Service.
    WARNING: Requires the actual Colab endpoint to be running!
    """
    pdf_path = tmp_path / "integration_test.pdf"
    pdf_path.write_bytes(MINIMAL_PDF_BYTES)
    
    pipeline = PDFChunkingPipeline()
    
    try:
        chunks = await pipeline.process_pdf(str(pdf_path))
        
        # It's possible a minimal PDF yields 0 structural chunks if Docling skips it,
        # but the HTTP request itself should succeed without crashing.
        assert isinstance(chunks, list), "Expected a list of chunks."
    except Exception as e:
        pytest.fail(f"Real remote PDF processing failed: {str(e)}")

