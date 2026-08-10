from .provider import LLMProvider
from .schemas import LLMStructuredIntent
from ..models.intent import AgentIntent
from .exceptions import LLMUnavailableError

class FakeLLMProvider(LLMProvider):
    """
    A mock LLM Provider for deterministic zero-cost testing.
    Instead of calling an API, it uses basic keyword checks to simulate LLM understanding of complex phrasing.
    """
    def __init__(self, fail_mode: bool = False):
        self.fail_mode = fail_mode

    def parse_command(self, text: str) -> LLMStructuredIntent:
        if self.fail_mode:
            raise LLMUnavailableError("Mock LLM is configured to fail.")
            
        lower_text = text.lower()
        
        # Deterministic simulation of an LLM understanding a write query
        if "update" in text or "change" in text or "set" in text or "move" in text:
            if "status" in text:
                return LLMStructuredIntent(
                    intent="UPDATE_ORDER_STATUS",
                    entities={"order_id": "OR603", "new_status": "pending"},
                    explanation="AI detected a complex status update request."
                )
            if "commitment date" in text or "date" in text:
                return LLMStructuredIntent(
                    intent="UPDATE_COMMITMENT_DATE",
                    entities={"order_id": "OR603", "new_commitment_date": "2026-08-15"},
                    explanation="AI detected a complex commitment date update request."
                )

        # Deterministic simulation of an LLM understanding a read query
        if "need my attention" in lower_text or "require action" in lower_text:
            return LLMStructuredIntent(
                intent=AgentIntent.LIST_ORDERS,
                confidence=0.92,
                entities={"status": "pending"},
                explanation="AI interpreted 'need my attention' as pending orders."
            )
            
        if "missing entity" in lower_text:
            return LLMStructuredIntent(
                intent=AgentIntent.NEEDS_CLARIFICATION,
                confidence=0.95,
                explanation="AI detected missing mandatory entities."
            )
            
        # Fallback to UNSUPPORTED for unknown complex phrases
        return LLMStructuredIntent(
            intent=AgentIntent.UNSUPPORTED,
            confidence=0.80,
            explanation="AI could not map this to a supported capability."
        )
