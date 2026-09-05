from abc import ABC, abstractmethod


class STTProvider(ABC):
    """Abstract Interface for Speech-to-Text providers."""

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, filename: str, content_type: str) -> str:
        """Transcribe an audio file to text. Returns the transcribed text."""
        pass
