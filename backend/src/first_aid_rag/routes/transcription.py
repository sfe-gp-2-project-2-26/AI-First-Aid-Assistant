from fastapi import APIRouter, Depends, File, UploadFile, status

from first_aid_rag.controllers.transcription_controller import TranscriptionController

router = APIRouter(tags=["Transcription"])


def get_transcription_controller() -> TranscriptionController:
    return TranscriptionController()


@router.post(
    "/transcribe",
    status_code=status.HTTP_200_OK,
    summary="Transcribe an audio recording to text (multipart field: file).",
)
async def transcribe_audio(
    file: UploadFile = File(...),
    controller: TranscriptionController = Depends(get_transcription_controller),
) -> dict:
    """Accepts a browser-recorded audio clip and returns {"text": "..."} for review in the chat input."""
    audio_bytes = await file.read()
    return await controller.transcribe(
        audio_bytes=audio_bytes,
        filename=file.filename or "recording.webm",
        content_type=file.content_type or "application/octet-stream",
    )
