import logging
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

# 25 MB is Groq's limit, but let's be conservative for voice commands
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

SUPPORTED_MIME_TYPES = [
    "audio/flac",
    "audio/mp3",
    "audio/mp4",
    "audio/mpeg",
    "audio/mpga",
    "audio/m4a",
    "audio/ogg",
    "audio/wav",
    "audio/webm"
]

class AudioValidator:
    @staticmethod
    async def validate(file: UploadFile) -> bytes:
        if not file.content_type:
            # Sometimes browser might not send content_type accurately, but we can fall back to checking extension if needed.
            # For this phase, we'll assume the browser sends it correctly.
            logger.warning("No content type provided for audio file.")
            
        elif file.content_type not in SUPPORTED_MIME_TYPES:
            # Browsers often send audio/webm or audio/ogg
            if not file.content_type.startswith("audio/"):
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
            
        audio_bytes = await file.read()
        
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file provided.")
            
        if len(audio_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Audio file exceeds maximum allowed size (5MB).")
            
        return audio_bytes
