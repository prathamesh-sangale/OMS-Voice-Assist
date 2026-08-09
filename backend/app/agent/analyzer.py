import re
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

class RuleEngineAnalyzer(CommandAnalyzer):
    """
    A scalable Rule-Based Engine that handles normalization, rule evaluation, and entity resolution.
    """
    def __init__(self, entity_resolver: EntityResolver):
        self._resolver = entity_resolver
        self._registry = RuleRegistry()
        
        # Register rules
        self._registry.register(GetOrderRule())
        self._registry.register(ListOrdersFilterRule())
        self._registry.register(ListOrdersGenericRule())
        self._registry.register(GetOrderTasksRule())
        self._registry.register(ListTasksRule())
        self._registry.register(ListCustomersRule())
        self._registry.register(GetOverviewRule())
        self._registry.register(GetAnalyticsRule())
        
    def analyze(self, command: CommandInput) -> IntentResult:
        # 1. Normalization
        text = TextNormalizer.normalize(command.text)
        
        # Security: Explicitly unsupported operations
        if "delete" in text or "update" in text or "create" in text or "add" in text:
            return IntentResult(
                intent=AgentIntent.UNSUPPORTED,
                confidence=1.0,
                explanation="Write operations are not supported in this phase."
            )
            
        if text in ["show the order", "show order"]:
            return IntentResult(
                intent=AgentIntent.NEEDS_CLARIFICATION,
                confidence=1.0,
                explanation="Order ID is missing."
            )
            
        # 2. Rule Match
        result = self._registry.evaluate(text)
        
        # 3. Entity Resolution (if applicable)
        if result.intent == AgentIntent.LIST_ORDERS and result.entities.get("sales_exec_candidate"):
            candidate = result.entities["sales_exec_candidate"]
            resolution = self._resolver.resolve_sales_exec(candidate)
            
            if resolution.is_ambiguous:
                return IntentResult(
                    intent=AgentIntent.NEEDS_CLARIFICATION,
                    confidence=1.0,
                    explanation=f"Found multiple matches for sales executive '{candidate}'. Which one do you mean?"
                )
            elif resolution.resolved_value:
                # Update the query contract
                result.query.sales_exec = resolution.resolved_value
                result.explanation += f" Resolved '{candidate}' to '{resolution.resolved_value}'."
            else:
                return IntentResult(
                    intent=AgentIntent.NEEDS_CLARIFICATION,
                    confidence=1.0,
                    explanation=f"Could not find any sales executive matching '{candidate}'."
                )
                
        return result
