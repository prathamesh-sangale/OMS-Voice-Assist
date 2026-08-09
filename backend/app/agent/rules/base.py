from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel
from ..models.command import IntentResult
from ..models.intent import AgentIntent

class CommandRule(ABC):
    """
    Abstract base class for all rules in the Rule Engine.
    """
    
    name: str
    intent: AgentIntent
    priority: int # Higher number = higher priority
    
    @abstractmethod
    def match(self, text: str) -> Optional[IntentResult]:
        """
        Attempts to match the normalized text.
        If matched, returns an IntentResult with extracted entities (unresolved).
        If not matched, returns None.
        """
        pass
