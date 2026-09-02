import logging
from typing import Optional

from first_aid_rag.config import settings
from first_aid_rag.interfaces.document_parser_interface import DocumentParser
from first_aid_rag.models.enums import DocumentParserType

logger = logging.getLogger(__name__)


class DocumentParserFactory:
    """Factory creating the configured DocumentParser implementation."""

    def create(self, provider_type: Optional[str] = None) -> DocumentParser:
        kind = provider_type or settings.DOCLING_PROVIDER_TYPE

        if kind == DocumentParserType.REMOTE.value:
            from first_aid_rag.stores.document_parser.providers.remote_docling import (
                DoclingProvider,
            )

            logger.info("DocumentParserFactory: using remote Docling provider.")
            return DoclingProvider()

        raise ValueError(f"Unsupported document parser type: {kind!r}")
