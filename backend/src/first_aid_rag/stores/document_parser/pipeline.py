import os
import hashlib
import logging
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
import httpx

from first_aid_rag.schemas.documents import ChunkMetadata, DocumentChunk
from first_aid_rag.interfaces.embedding_interface import EmbeddingProvider
from first_aid_rag.config import settings

logger = logging.getLogger(__name__)

# Constants and Headers
REMOTE_HEADERS = {
    "ngrok-skip-browser-warning": "true",
    "User-Agent": "ClinicalRAG-Client/1.0",
}

CONTENT_ROLE_MAP = {
    "key_action": ["key action", "key actions", "action required", "immediate action", "action", "actions"],
    "access_help": ["access help", "call emergency", "emergency help", "when to call", "emergency", "assistance", "help"],
    "caution": ["caution", "warning", "warnings", "risk", "risks", "danger", "dangers", "contraindication", "contraindications", "do not"],
    "recovery": ["recovery", "aftercare", "post-care", "follow-up", "monitoring"],
    "first_aid_steps": ["first aid", "first-aid", "first aid steps", "initial steps", "step", "steps"],
    "good_practice": ["good practice", "best practice", "practice point", "practice points", "good_practice"],
    "education": ["education", "prevention", "training", "awareness"],
    "scientific_foundation": ["scientific foundation", "scientific", "evidence", "rationale", "rationales", "foundation", "foundations"],
    "introduction": ["introduction", "overview", "background", "scope", "about this guideline", "about"],
}

class PDFChunkingPipeline:
    """
    Remote Pipeline for Medical / Clinical RAG.
    
    Modes:
      - Remote:
          1. Upload PDF to remote /chunk_pdf endpoint.
          2. Enrich metadata locally.
          3. POST to remote /embed endpoint.
    """

    def __init__(
        self,
        source_type: str = "clinical_guideline",
        document_version: str = "2025",
        language: str = "en",
    ):
        self.source_type = source_type
        self.document_version = document_version
        self.language = language

    def _derive_content_role(self, heading_path: List[str]) -> Optional[str]:
        """Rule-based content_role lookup against the last 1-2 entries of heading_path."""
        if not heading_path:
            return None

        relevant_headers = heading_path[-2:]
        combined_header_text = " ".join(relevant_headers).lower()

        for role_name, keywords in CONTENT_ROLE_MAP.items():
            for kw in keywords:
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, combined_header_text):
                    return role_name

        return None

    def _map_content_type(self, doc_item_labels: List[str]) -> str:
        """Map doc_item_labels to 'text' | 'table' | 'figure'. Fall back to 'text' if unclear."""
        if not doc_item_labels:
            return "text"

        labels_lower = [str(lbl).lower() for lbl in doc_item_labels]
        has_table = any("table" in lbl for lbl in labels_lower)
        has_figure = any("picture" in lbl or "figure" in lbl or "caption" in lbl for lbl in labels_lower)

        if has_table and not has_figure:
            return "table"
        if has_figure and not has_table:
            return "figure"
        if has_table and has_figure:
            logger.warning(f"⚠️ Chunk has mixed labels ({doc_item_labels}). Falling back to 'text'.")
            return "text"

        return "text"

    def _calculate_token_count(self, text: str) -> int:
        """Basic word count estimation since local tokenizers are disabled."""
        return len(text.split())

    async def process_pdf(
        self,
        pdf_path: str,
        embedding_provider: Optional[EmbeddingProvider] = None,
    ) -> List[DocumentChunk]:
        """Process PDF by delegating chunking and embedding to remote URL."""
        if not settings.EMBEDDING_URL:
            raise ValueError("EMBEDDING_URL is not set. Remote processing requires this configuration.")
            
        logger.info(f"Delegating PDF processing to remote URL: {settings.EMBEDDING_URL}")
        
        path_obj = Path(pdf_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        pdf_bytes = path_obj.read_bytes()
        document_id = hashlib.sha256(pdf_bytes).hexdigest()
        document_title = path_obj.stem
        source_name = path_obj.name

        remote_base_url = settings.EMBEDDING_URL.rstrip("/")
        chunk_pdf_url = f"{remote_base_url}/chunk_pdf"
        embed_url = f"{remote_base_url}/embed"

        logger.info(f"📄 Uploading '{source_name}' (ID: {document_id[:10]}...) to remote chunker '{chunk_pdf_url}'...")
        async with httpx.AsyncClient(timeout=180.0) as client:
            files = {"file": (source_name, pdf_bytes, "application/pdf")}
            res = await client.post(chunk_pdf_url, files=files, headers=REMOTE_HEADERS)
            if res.status_code != 200:
                raise RuntimeError(f"Remote /chunk_pdf failed ({res.status_code}): {res.text}")
            
            chunk_data = res.json()

        raw_chunks = chunk_data.get("chunks", [])
        total_pages = chunk_data.get("total_pages", 1)
        chunk_count = chunk_data.get("chunk_count", len(raw_chunks))
        logger.info(f"✅ Received {chunk_count} structural chunks across {total_pages} pages from remote service.")

        if not raw_chunks:
            logger.warning("No structural chunks returned from remote /chunk_pdf service.")
            return []

        chunk_objects_metadata: List[Dict[str, Any]] = []
        texts_for_embedding: List[str] = []

        for item in raw_chunks:
            chunk_idx = item.get("chunk_index", len(chunk_objects_metadata))
            text = item.get("text", "")
            contextualized_text = item.get("contextualized_text") or text

            if not text.strip():
                continue

            chunk_id = f"{document_id}_chunk_{chunk_idx:05d}"
            headings = item.get("headings", [])
            pages = item.get("pages", [])
            doc_item_labels = item.get("doc_item_labels", [])

            content_type = self._map_content_type(doc_item_labels)
            section = headings[0] if headings else None
            subsection = headings[1] if len(headings) > 1 else None
            content_role = self._derive_content_role(headings)

            token_count = self._calculate_token_count(text)
            content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

            first_page = pages[0] if (pages and len(pages) > 0) else 1
            meta = ChunkMetadata(
                chunk_id=chunk_id,
                document_id=document_id,
                document_title=document_title,
                source=source_name,
                source_type=self.source_type,
                document_version=self.document_version,
                language=self.language,
                content_type=content_type,
                pdf_pages=pages,
                pdf_page=first_page,
                document_page=first_page,
                heading_path=headings,
                section=section,
                subsection=subsection,
                content_role=content_role,
                token_count=token_count,
                chunk_index=chunk_idx,
                content_hash=content_hash,
            )

            chunk_objects_metadata.append({
                "chunk_id": chunk_id,
                "text": text,
                "contextualized_text": contextualized_text,
                "metadata": meta,
            })
            texts_for_embedding.append(contextualized_text)

        logger.info(f"🌐 Sending {len(texts_for_embedding)} contextualized texts to remote embed endpoint '{embed_url}'...")
        async with httpx.AsyncClient(timeout=180.0) as client:
            res = await client.post(embed_url, json={"texts": texts_for_embedding}, headers=REMOTE_HEADERS)
            if res.status_code != 200:
                raise RuntimeError(f"Remote /embed endpoint failed ({res.status_code}): {res.text}")
            
            embed_response = res.json()

        dense_vectors = embed_response.get("dense", []) if isinstance(embed_response, dict) else []
        sparse_objects = embed_response.get("sparse", []) if isinstance(embed_response, dict) else []
        legacy_embeddings = embed_response if isinstance(embed_response, list) else embed_response.get("embeddings", [])

        final_document_chunks: List[DocumentChunk] = []
        for idx, item in enumerate(chunk_objects_metadata):
            dense_vec = None
            sparse_indices = None
            sparse_values = None

            if dense_vectors and idx < len(dense_vectors):
                dense_vec = dense_vectors[idx]
                if sparse_objects and idx < len(sparse_objects):
                    sparse_info = sparse_objects[idx] or {}
                    sparse_indices = sparse_info.get("indices") or sparse_info.get("sparse_indices")
                    sparse_values = sparse_info.get("values") or sparse_info.get("sparse_values")
            elif legacy_embeddings and idx < len(legacy_embeddings):
                vec_data = legacy_embeddings[idx] or {}
                dense_vec = vec_data.get("dense")
                sparse_indices = vec_data.get("sparse_indices") or vec_data.get("indices")
                sparse_values = vec_data.get("sparse_values") or vec_data.get("values")

            final_chunk = DocumentChunk(
                chunk_id=item["chunk_id"],
                text=item["text"],
                metadata=item["metadata"],
                dense_vector=dense_vec,
                sparse_indices=sparse_indices,
                sparse_values=sparse_values,
            )
            final_document_chunks.append(final_chunk)

        logger.info(f"🚀 Successfully generated {len(final_document_chunks)} ready-to-index DocumentChunk objects!")
        return final_document_chunks

