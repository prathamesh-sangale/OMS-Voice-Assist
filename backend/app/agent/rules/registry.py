import logging
from typing import List
from .base import CommandRule
from ..models.command import IntentResult

logger = logging.getLogger(__name__)

class RuleRegistry:
    """
    Holds a collection of CommandRules and evaluates them in priority order.
    """
    def __init__(self):
        self._rules: List[CommandRule] = []
        
    def register(self, rule: CommandRule):
        self._rules.append(rule)
        # Sort so highest priority comes first
        self._rules.sort(key=lambda r: r.priority, reverse=True)
        
    def evaluate(self, normalized_text: str) -> IntentResult:
        """
        Evaluates rules sequentially. Returns the first matching IntentResult.
        """
        for rule in self._rules:
            result = rule.match(normalized_text)
            if result:
                logger.debug(f"Rule '{rule.name}' matched text '{normalized_text}'")
                return result
                
        from ..models.intent import AgentIntent
        return IntentResult(
            intent=AgentIntent.UNSUPPORTED,
            confidence=0.0,
            explanation="No matching rule found in registry."
        )
