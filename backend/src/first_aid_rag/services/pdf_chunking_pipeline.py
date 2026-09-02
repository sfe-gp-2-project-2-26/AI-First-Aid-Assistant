"""
Backward compatibility re-export for PDFChunkingPipeline.
The pipeline implementation is maintained under `first_aid_rag.stores.document_parser.pipeline`.
"""

from first_aid_rag.stores.document_parser.pipeline import (
    PDFChunkingPipeline,
    REMOTE_HEADERS,
    CONTENT_ROLE_MAP,
)

__all__ = [
    "PDFChunkingPipeline",
    "REMOTE_HEADERS",
    "CONTENT_ROLE_MAP",
]
