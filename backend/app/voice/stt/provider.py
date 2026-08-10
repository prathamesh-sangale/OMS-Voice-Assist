from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

class TranscriptResponse(BaseModel):
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    provider: str
    model: str
    confidence: Optional[float] = None

class STTProvider(ABC):
    """
    Abstract base class for Speech-to-Text providers.
    """
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, filename: str) -> TranscriptResponse:
        pass
