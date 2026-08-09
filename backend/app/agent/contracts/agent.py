from abc import ABC, abstractmethod
from ..models.command import CommandInput, IntentResult

class CommandAnalyzer(ABC):
    """Abstract interface for all agent analyzers (deterministic, rule-based, or LLM)."""
    
    @abstractmethod
    def analyze(self, command: CommandInput) -> IntentResult:
        """Analyze a natural language command and return a structured IntentResult."""
        pass
