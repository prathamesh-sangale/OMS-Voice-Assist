from typing import Optional
from .base import CommandRule
from ..models.command import IntentResult
from ..models.intent import AgentIntent
from ...oms.contracts.queries import CustomerQuery

class ListCustomersRule(CommandRule):
    name = "ListCustomersRule"
    intent = AgentIntent.LIST_CUSTOMERS
    priority = 85
    
    def match(self, text: str) -> Optional[IntentResult]:
        if text in ["show customers", "list customers", "show customer list"]:
            return IntentResult(
                intent=self.intent,
                confidence=0.85,
                query=CustomerQuery(),
                explanation="Generic list customers match."
            )
        return None
