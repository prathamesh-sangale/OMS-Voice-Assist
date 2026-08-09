from typing import Optional
from .base import CommandRule
from ..models.command import IntentResult
from ..models.intent import AgentIntent

class GetOverviewRule(CommandRule):
    name = "GetOverviewRule"
    intent = AgentIntent.GET_OVERVIEW
    priority = 85
    
    def match(self, text: str) -> Optional[IntentResult]:
        keywords = ["show overview", "show dashboard", "give me an overview", "what is happening", "give me the current summary"]
        if text in keywords:
            return IntentResult(
                intent=self.intent,
                confidence=0.90,
                explanation="Matched dashboard/overview keyword."
            )
        return None
