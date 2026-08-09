from typing import Optional
from .base import CommandRule
from ..models.command import IntentResult
from ..models.intent import AgentIntent

class GetAnalyticsRule(CommandRule):
    name = "GetAnalyticsRule"
    intent = AgentIntent.GET_ANALYTICS
    priority = 85
    
    def match(self, text: str) -> Optional[IntentResult]:
        keywords = ["show analytics", "show order analytics", "give me analytics", "show order distribution", "show business model distribution"]
        if text in keywords:
            return IntentResult(
                intent=self.intent,
                confidence=0.90,
                explanation="Matched analytics keyword."
            )
        return None
