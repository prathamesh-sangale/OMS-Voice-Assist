import re
from typing import Optional
from .base import CommandRule
from ..models.command import IntentResult
from ..models.intent import AgentIntent
from ...oms.contracts.queries import OrderQuery
from ..normalization.order_id import normalize_order_id

class PositionalReferenceRule(CommandRule):
    name = "PositionalReferenceRule"
    intent = AgentIntent.GET_ORDER
    priority = 110 # Very high priority to catch specific positional context
    
    def match(self, text: str) -> Optional[IntentResult]:
        words_to_index = {
            "first": 0,
            "second": 1,
            "third": 2,
            "fourth": 3,
            "fifth": 4,
            "last": -1
        }
        
        text_lower = text.lower()
        for word, idx in words_to_index.items():
            if re.search(rf"\b{word}\b", text_lower):
                # Only trigger if they want to view/act on it
                if any(v in text_lower for v in ["show", "open", "get", "tell", "change", "update", "set", "move", "the"]):
                    return IntentResult(
                        intent=self.intent, # We default to GET_ORDER, but target_resolver will use it
                        confidence=0.9,
                        entities={
                            "position_index": idx
                        },
                        explanation=f"Rule Engine extracted positional reference: {word}"
                    )
        return None

class GetOrderRule(CommandRule):
    name = "GetOrderRule"
    intent = AgentIntent.GET_ORDER
    priority = 100 # Highest priority for specific IDs
    
    def match(self, text: str) -> Optional[IntentResult]:
        # Match OR123, or 123, order 123, order number 123, etc.
        match = re.search(r"\b(?:or|order(?:(?:\s+number|\s+no\.?)?))?\s*[\-]?\s*(\d+)\b", text, re.IGNORECASE)
        if match and any(verb in text for verb in ["show", "open", "get", "tell"]):
            order_id = normalize_order_id(match.group(1))
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
            
        id_match = re.search(r"\b(?:or|order(?:(?:\s+number|\s+no\.?)?))?\s*[\-]?\s*(\d+)\b", text, re.IGNORECASE)
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
                        "order_id": normalize_order_id(id_match.group(1)),
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
            
        id_match = re.search(r"\b(?:or|order(?:(?:\s+number|\s+no\.?)?))?\s*[\-]?\s*(\d+)\b", text, re.IGNORECASE)
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
                        "order_id": normalize_order_id(id_match.group(1)),
                        "new_commitment_date_candidate": date_match.group(1).strip()
                    },
                    explanation="Rule Engine extracted a commitment date update request."
                )
        return None

class UpdateOrderDestinationRule(CommandRule):
    name = "UpdateOrderDestinationRule"
    intent = AgentIntent.UPDATE_ORDER_DESTINATION
    priority = 110
    
    def match(self, text: str) -> Optional[IntentResult]:
        if "update" not in text and "set" not in text and "change" not in text:
            return None
            
        if "destination" in text or "delivery city" in text:
            id_match = re.search(r"\b(?:or|order(?:(?:\s+number|\s+no\.?)?))?\s*[\-]?\s*(\d+)\b", text, re.IGNORECASE)
            order_id = id_match.group(1).upper() if id_match else None
            
            # E.g. "change destination to Mumbai"
            dest_match = re.search(r"to\s+([a-zA-Z\s]+)", text)
            
            entities = {}
            if order_id:
                entities["order_id"] = normalize_order_id(order_id)
            if dest_match:
                # "Mumbai" might be matched along with other words, but simple is okay for demo
                val = dest_match.group(1).strip()
                # Stop words hack for simple rule
                val = val.replace(" for", "").replace(" please", "")
                entities["new_destination"] = val
                
            return IntentResult(
                intent=self.intent,
                confidence=0.8,
                entities=entities,
                explanation="Rule Engine extracted a destination update request."
            )
        return None
