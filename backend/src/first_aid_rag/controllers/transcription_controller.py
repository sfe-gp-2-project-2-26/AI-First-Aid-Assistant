import logging
from typing import Optional

from fastapi import HTTPException, status

from first_aid_rag.interfaces.stt_interface import STTProvider
from first_aid_rag.stores.stt.factory import STTFactory

logger = logging.getLogger(__name__)

MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB


class TranscriptionController:
    """Controller handling audio transcription requests."""

    def __init__(self, stt_provider: Optional[STTProvider] = None):
        self.stt_provider = stt_provider or STTFactory().create()

    async def transcribe(self, audio_bytes: bytes, filename: str, content_type: str) -> dict:
        if not audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Audio file is empty.",
            )
        if len(audio_bytes) > MAX_AUDIO_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Audio file exceeds the 25 MB limit.",
            )

        try:
            text = await self.stt_provider.transcribe(audio_bytes, filename, content_type)
            return {"text": text}
        except RuntimeError as e:
            logger.error("Transcription failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(e),
            )
