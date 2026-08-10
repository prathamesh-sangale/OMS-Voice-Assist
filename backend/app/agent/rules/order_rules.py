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
    priority = 10 
    
    def match(self, text: str) -> Optional[IntentResult]:
        if "order" in text and any(verb in text for verb in ["show", "list", "get", "all"]):
            return IntentResult(
                intent=self.intent,
                confidence=0.7,
                explanation="AI detected a generic request for orders."
            )
        return None

class UpdateOrderStatusRule(CommandRule):
    name = "UpdateOrderStatusRule"
    intent = AgentIntent.UPDATE_ORDER_STATUS
    priority = 110 # High priority for writes
    
    def match(self, text: str) -> Optional[IntentResult]:
        if "update" not in text and "set" not in text and "change" not in text:
            return None
            
        id_match = re.search(r"\b(or\d+)\b", text)
        if not id_match:
            return None
            
        if "status" in text:
            # Try to extract the status value (e.g. "update OR603 status to pending")
            status_match = re.search(r"status\s+(?:to\s+)?([a-z]+)", text)
            if status_match:
                return IntentResult(
                    intent=self.intent,
                    confidence=1.0,
                    entities={
                        "order_id": id_match.group(1).upper(),
                        "new_status": status_match.group(1)
                    },
                    explanation="Rule Engine extracted an order status update request."
                )
        return None

class UpdateOrderCommitmentDateRule(CommandRule):
    name = "UpdateOrderCommitmentDateRule"
    intent = AgentIntent.UPDATE_COMMITMENT_DATE
    priority = 110
    
    def match(self, text: str) -> Optional[IntentResult]:
        if "update" not in text and "set" not in text and "change" not in text and "move" not in text:
            return None
            
        id_match = re.search(r"\b(or\d+)\b", text)
        if not id_match:
            return None
            
        if "commitment date" in text or "date" in text:
            # E.g. "update or615 commitment date to 2026-08-15"
            date_match = re.search(r"to\s+(\d{4}-\d{2}-\d{2}|[a-z0-9\s]+)", text)
            if date_match:
                return IntentResult(
                    intent=self.intent,
                    confidence=1.0,
                    entities={
                        "order_id": id_match.group(1).upper(),
                        "new_commitment_date_candidate": date_match.group(1).strip()
                    },
                    explanation="Rule Engine extracted a commitment date update request."
                )
        return None
