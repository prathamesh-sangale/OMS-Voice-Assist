import re
from typing import Optional
from .base import CommandRule
from ..models.command import IntentResult
from ..models.intent import AgentIntent
from ...oms.contracts.queries import TaskQuery

class GetOrderTasksRule(CommandRule):
    name = "GetOrderTasksRule"
    intent = AgentIntent.GET_ORDER_TASKS
    priority = 105 
    
    def match(self, text: str) -> Optional[IntentResult]:
        if "task" in text or "workflow" in text:
            match = re.search(r"\b(or\d+)\b", text, re.IGNORECASE)
            if match:
                order_id = match.group(1).upper()
                return IntentResult(
                    intent=self.intent,
                    confidence=0.95,
                    entities={"order_id": order_id},
                    query=order_id,
                    explanation=f"Tasks for specific order {order_id}"
                )
        return None

class ListTasksRule(CommandRule):
    name = "ListTasksRule"
    intent = AgentIntent.LIST_TASKS
    priority = 85
    
    def match(self, text: str) -> Optional[IntentResult]:
        if "task" not in text:
            return None
            
        status = None
        if "pending" in text:
            status = "pending"
        elif "completed" in text:
            status = "completed"
            
        department = None
        if "logistics" in text:
            department = "logistics"
        elif "finance" in text:
            department = "finance"
            
        if status or department:
            return IntentResult(
                intent=self.intent,
                confidence=0.90,
                entities={"status": status, "department": department},
                query=TaskQuery(status=status, department=department),
                explanation="Filtered task search."
            )
            
        if text in ["show tasks", "list tasks"]:
            return IntentResult(
                intent=self.intent,
                confidence=0.85,
                query=TaskQuery(),
                explanation="Generic list tasks match."
            )
            
        return None
