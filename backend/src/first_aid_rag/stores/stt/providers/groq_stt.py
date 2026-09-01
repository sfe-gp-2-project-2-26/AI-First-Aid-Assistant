import logging

import httpx

from first_aid_rag.config import settings
from first_aid_rag.interfaces.stt_interface import STTProvider

logger = logging.getLogger(__name__)

GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


class GroqSTTProvider(STTProvider):
    """Speech-to-text via Groq's hosted Whisper (whisper-large-v3 by default)."""

    def __init__(
        self,
        api_key: str = settings.GROQ_API_KEY,
        model: str = settings.GROQ_STT_MODEL,
        timeout: int = settings.STT_TIMEOUT,
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def transcribe(self, audio_bytes: bytes, filename: str, content_type: str) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                GROQ_TRANSCRIPTION_URL,
                headers={"Authorization": f"Bearer {self.api_key}"},
                data={"model": self.model},
                files={"file": (filename, audio_bytes, content_type)},
            )

        if response.status_code != 200:
            logger.error("Groq transcription failed: HTTP %d %s", response.status_code, response.text[:300])
            raise RuntimeError(f"Transcription provider error (HTTP {response.status_code}).")

        text = (response.json().get("text") or "").strip()
        logger.info("Transcribed %d bytes -> %d chars.", len(audio_bytes), len(text))
        return text
