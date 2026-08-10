from abc import ABC, abstractmethod

class TTSProvider(ABC):
    """
    Abstract base class for Text-to-Speech providers.
    """
    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        pass
