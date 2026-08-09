import re
from typing import Optional
from .base import CommandRule
from ..models.command import IntentResult
from ..models.intent import AgentIntent
from ...oms.contracts.queries import OrderQuery

class GetOrderRule(CommandRule):
    name = "GetOrderRule"
    intent = AgentIntent.GET_ORDER
    priority = 100 # Highest priority for specific IDs
    
    def match(self, text: str) -> Optional[IntentResult]:
        # OR followed by digits
        match = re.search(r"\b(or\d+)\b", text, re.IGNORECASE)
        if match and any(verb in text for verb in ["show", "open", "get", "tell"]):
            order_id = match.group(1).upper()
            return IntentResult(
                intent=self.intent,
                confidence=0.99,
                entities={"order_id": order_id},
                query=order_id,
                explanation=f"Explicitly extracted order ID: {order_id}"
            )
        return None

class ListOrdersFilterRule(CommandRule):
    name = "ListOrdersFilterRule"
    intent = AgentIntent.LIST_ORDERS
    priority = 90
    
    def match(self, text: str) -> Optional[IntentResult]:
        if "order" not in text:
            return None
            
        status = None
        if "pending" in text:
            status = "pending"
        elif "completed" in text or "complete" in text:
            status = "completed"
            
        business_model = None
        if "rental" in text:
            business_model = "Rental"
        elif "sale" in text:
            business_model = "Sale"
        elif "lease" in text:
            business_model = "Lease"
            
        product = None
        if "reefer" in text:
            product = "Reefer Container"
            
        sales_exec = None
        match = re.search(r"orders for ([\w\s]+)", text)
        if match:
            candidate = match.group(1).strip()
            # We don't resolve here, we just extract. The Engine handles resolution.
            if candidate not in ["pending", "completed", "rental", "sale", "lease", "reefer"]:
                sales_exec = candidate

        if status or business_model or product or sales_exec:
            return IntentResult(
                intent=self.intent,
                confidence=0.90,
                entities={"status": status, "business_model": business_model, "product": product, "sales_exec_candidate": sales_exec},
                query=OrderQuery(status=status, business_model=business_model, product=product),
                explanation="Matched order filters."
            )
        return None

class ListOrdersGenericRule(CommandRule):
    name = "ListOrdersGenericRule"
    intent = AgentIntent.LIST_ORDERS
    priority = 80
    
    def match(self, text: str) -> Optional[IntentResult]:
        if text in ["show orders", "list orders", "get orders", "show me orders", "display orders"]:
            return IntentResult(
                intent=self.intent,
                confidence=0.85,
                query=OrderQuery(),
                explanation="Generic list orders match."
            )
        return None
