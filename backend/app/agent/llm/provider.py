from abc import ABC, abstractmethod
from .schemas import LLMStructuredIntent

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    """
    @abstractmethod
    def parse_command(self, text: str, session_context: dict = None) -> LLMStructuredIntent:
        """
        Interprets a natural language command and returns a structured intent.
        Optionally takes the current session_context for conversational modifications.
        Raises LLMException on failure.
        """
        pass
