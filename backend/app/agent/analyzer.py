import re
import logging
from typing import Optional

from .contracts.agent import CommandAnalyzer
from .models.command import CommandInput, IntentResult
from .models.intent import AgentIntent

from .normalization.text_normalizer import TextNormalizer
from .resolution.entity_resolver import EntityResolver
from .rules.registry import RuleRegistry
from .rules.order_rules import GetOrderRule, ListOrdersFilterRule, ListOrdersGenericRule
from .rules.task_rules import GetOrderTasksRule, ListTasksRule
from .rules.customer_rules import ListCustomersRule
from .rules.overview_rules import GetOverviewRule
from .rules.analytics_rules import GetAnalyticsRule

from .llm.provider import LLMProvider
from .llm.exceptions import LLMException
from ..oms.contracts.queries import OrderQuery, TaskQuery, CustomerQuery

logger = logging.getLogger(__name__)

class HybridAnalyzer(CommandAnalyzer):
    """
    A Hybrid Engine that routes between deterministic rules and an LLM fallback.
    """
    def __init__(self, entity_resolver: EntityResolver, llm_provider: LLMProvider):
        self._resolver = entity_resolver
        self._llm = llm_provider
        self._registry = RuleRegistry()
        
        # Register rules
        from .rules.order_rules import PositionalReferenceRule
        self._registry.register(PositionalReferenceRule())
        self._registry.register(GetOrderRule())
        self._registry.register(ListOrdersFilterRule())
        self._registry.register(ListOrdersGenericRule())
        self._registry.register(GetOrderTasksRule())
        self._registry.register(ListTasksRule())
        self._registry.register(ListCustomersRule())
        self._registry.register(GetOverviewRule())
        self._registry.register(GetAnalyticsRule())
        from .rules.order_rules import UpdateOrderStatusRule, UpdateOrderCommitmentDateRule, UpdateOrderDestinationRule
        self._registry.register(UpdateOrderStatusRule())
        self._registry.register(UpdateOrderCommitmentDateRule())
        self._registry.register(UpdateOrderDestinationRule())
        
        from .rules.navigation_rules import NavigationRule
        self._registry.register(NavigationRule())
        
    def analyze(self, command: CommandInput, session=None) -> IntentResult:
        # 0. System commands interception
        raw_text = command.text.strip()
        if raw_text.startswith("!confirm "):
            parts = raw_text.split(" ", 1)
            if len(parts) == 2:
                return IntentResult(
                    intent=AgentIntent.CONFIRM_ACTION,
                    confidence=1.0,
                    entities={"confirmation_id": parts[1].strip()},
                    metadata={"method": "System"}
                )
        if raw_text.startswith("!cancel "):
            parts = raw_text.split(" ", 1)
            if len(parts) == 2:
                return IntentResult(
                    intent=AgentIntent.CANCEL_ACTION,
                    confidence=1.0,
                    entities={"confirmation_id": parts[1].strip()},
                    metadata={"method": "System"}
                )
                
        # 1. Normalization
        text = TextNormalizer.normalize(command.text)
        text_lower = text.lower()
        
        # Undo / Cancel interception
        if text_lower in ["reset the change", "undo", "revert"]:
            if session and session.context.operation_status == "pending_confirmation":
                return IntentResult(
                    intent=AgentIntent.CANCEL_ACTION,
                    confidence=1.0,
                    entities={"confirmation_id": session.context.confirmation_id},
                    metadata={"method": "System"}
                )
            else:
                return IntentResult(
                    intent=AgentIntent.UNSUPPORTED,
                    confidence=1.0,
                    explanation="I can't automatically undo that completed change yet.",
                    metadata={"method": "System"}
                )
        
        # Security: Explicitly unsupported operations blocked before LLM
        if "delete" in text or "create" in text or "add" in text:
            return IntentResult(
                intent=AgentIntent.UNSUPPORTED,
                confidence=1.0,
                explanation="Delete and Create operations are not supported in this phase.",
                metadata={"method": "Security Policy"}
            )
            
        if text in ["show the order", "show order"]:
            return IntentResult(
                intent=AgentIntent.NEEDS_CLARIFICATION,
                confidence=1.0,
                explanation="Order ID is missing.",
                metadata={"method": "Rule Engine"}
            )
            
        # 2. Rule Match
        result = self._registry.evaluate(text)
        
        # 3. LLM Fallback (if Rule Engine yields UNSUPPORTED with 0 confidence)
        if result.intent == AgentIntent.UNSUPPORTED and result.confidence == 0.0:
            logger.info("Rule Engine could not resolve command. Falling back to LLM.")
            try:
                context_dict = session.context.last_result_context.get("query") if (session and session.context.last_result_context) else None
                llm_intent = self._llm.parse_command(command.text, session_context=context_dict)
                
                # Convert LLMStructuredIntent to IntentResult and generate Query Contract
                result = IntentResult(
                    intent=llm_intent.intent,
                    confidence=llm_intent.confidence,
                    entities=llm_intent.entities,
                    explanation=llm_intent.explanation,
                    metadata={"method": "AI"}
                )
                self._attach_query_contract(result)
            except LLMException as e:
                logger.error(f"LLM Fallback failed: {e}")
                return IntentResult(
                    intent=AgentIntent.UNSUPPORTED,
                    confidence=1.0,
                    explanation="The advanced command service is currently unavailable. Please try a standard OMS command.",
                    metadata={"method": "AI Fallback Error"}
                )
        else:
            if not result.metadata:
                result.metadata = {}
            result.metadata["method"] = "Rule Engine"
        
        # 4. Entity Resolution (if applicable)
        if result.intent == AgentIntent.LIST_ORDERS and result.entities.get("sales_exec_candidate"):
            candidate = result.entities["sales_exec_candidate"]
            resolution = self._resolver.resolve_sales_exec(candidate)
            
            if resolution.is_ambiguous:
                return IntentResult(
                    intent=AgentIntent.NEEDS_CLARIFICATION,
                    confidence=1.0,
                    explanation=f"Found multiple matches for sales executive '{candidate}'. Which one do you mean?",
                    metadata=result.metadata
                )
            elif resolution.resolved_value:
                # Ensure query exists
                if not result.query:
                    result.query = OrderQuery()
                result.query.sales_exec = resolution.resolved_value
                result.explanation += f" Resolved '{candidate}' to '{resolution.resolved_value}'."
            else:
                return IntentResult(
                    intent=AgentIntent.NEEDS_CLARIFICATION,
                    confidence=1.0,
                    explanation=f"Could not find any sales executive matching '{candidate}'.",
                    metadata=result.metadata
                )
                
        return result

    def _attach_query_contract(self, result: IntentResult):
        """Attaches the correct Query object based on LLM intent."""
        if result.intent == AgentIntent.LIST_ORDERS:
            result.query = OrderQuery(
                status=result.entities.get("status"),
                business_model=result.entities.get("business_model"),
                product=result.entities.get("product")
            )
        elif result.intent == AgentIntent.LIST_TASKS:
            result.query = TaskQuery(
                status=result.entities.get("status"),
                department=result.entities.get("department")
            )
        elif result.intent == AgentIntent.LIST_CUSTOMERS:
            result.query = CustomerQuery()
        elif result.intent in [AgentIntent.GET_ORDER, AgentIntent.GET_ORDER_TASKS]:
            if "order_id" in result.entities:
                result.query = result.entities["order_id"]
