from typing import Any
from ..models.intent import AgentIntent

class ResponseFormatter:
    """Converts OMS result payloads into human readable text."""
    
    @staticmethod
    def format_success(intent: AgentIntent, data: Any) -> str:
        if intent == AgentIntent.LIST_ORDERS:
            return f"I found {data.total} orders matching your criteria."
            
        if intent == AgentIntent.GET_ORDER:
            return f"Here are the details for order {data.order_number}."
            
        if intent == AgentIntent.LIST_TASKS:
            return f"I found {data.total} tasks."
            
        if intent == AgentIntent.GET_ORDER_TASKS:
            return f"I found {len(data)} tasks for that order."
            
        if intent == AgentIntent.LIST_CUSTOMERS:
            return f"I found {data.total} customers matching your criteria."
            
        if intent == AgentIntent.GET_OVERVIEW:
            return "Here is the executive overview."
            
        if intent == AgentIntent.GET_ANALYTICS:
            return "Here is the analytical distribution."
            
        return "Command executed successfully."

    @staticmethod
    def format_error(error_msg: str) -> str:
        return f"Sorry, I encountered an error: {error_msg}"
        
    @staticmethod
    def format_not_found(entity_id: str) -> str:
        return f"I could not find the record: {entity_id}"
