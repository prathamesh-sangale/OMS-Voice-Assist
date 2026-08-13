import os
import logging
from typing import Optional
from groq import Groq
from pydantic import BaseModel
from .provider import STTProvider, TranscriptResponse

logger = logging.getLogger(__name__)

class GroqSTTException(Exception):
    pass

class GroqWhisperProvider(STTProvider):
    """
    Implementation of STTProvider using Groq's whisper-large-v3-turbo.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-large-v3-turbo"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo")
        
        if not self.api_key:
            # We don't raise here immediately, we handle it gracefully when transcribe is called
            self.client = None
            logger.warning("GROQ_API_KEY is not set. Voice transcription will fail.")
        else:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                self.client = None
                logger.error(f"Failed to initialize Groq client: {e}")

    def transcribe(self, audio_bytes: bytes, filename: str) -> TranscriptResponse:
        if not self.client:
            raise GroqSTTException("STT Provider is not configured (missing API key).")
            
        try:
            logger.info(f"Sending audio ({len(audio_bytes)} bytes) to Groq STT model: {self.model}")
            
            # Groq Python SDK expects a tuple of (filename, bytes) or similar for the file parameter
            file_tuple = (filename, audio_bytes)
            
            transcription = self.client.audio.transcriptions.create(
                file=file_tuple,
                model=self.model,
                response_format="verbose_json",
                temperature=0.0,
                language="en",
                prompt="OMS, orders, dry container, reefer container, ISO tank, client, Acme, refer, order, container."
            )
            
            # Safely extract values since they might not be present
            text = getattr(transcription, 'text', '').strip()
            
            # Filter known Whisper silence hallucinations
            hallucinations = ["thank you.", "thank you", "спасибо.", "hello.", "hello", "you", "thanks for watching", "thanks for watching.", ""]
            if text.lower() in hallucinations:
                text = ""
                
            language = getattr(transcription, 'language', None)
            duration = getattr(transcription, 'duration', None)
            
            return TranscriptResponse(
                text=text.strip(),
                language=language,
                duration=duration,
                provider="Groq",
                model=self.model,
                confidence=None  # Groq Whisper does not reliably provide word-level confidence in the basic response
            )
            
        except Exception as e:
            logger.error(f"Groq transcription failed: {e}")
            raise GroqSTTException(f"Transcription failed: {str(e)}")
