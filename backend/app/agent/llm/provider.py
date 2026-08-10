from abc import ABC, abstractmethod
from .schemas import LLMStructuredIntent

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    """
    @abstractmethod
    def parse_command(self, text: str) -> LLMStructuredIntent:
        """
        Interprets a natural language command and returns a structured intent.
        Raises LLMException on failure.
        """
        pass
