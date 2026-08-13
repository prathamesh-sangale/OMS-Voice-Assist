from typing import Any, Tuple
from ..models.intent import AgentIntent

class ResponseFormatter:
    """Formats raw data into user-friendly UI responses and concise spoken TTS responses."""
    
    @staticmethod
    def format_success(intent: AgentIntent, data: Any) -> Tuple[str, str]:
        if intent == AgentIntent.LIST_ORDERS:
            message = f"I found {data.total} orders matching your criteria."
            return message, message
            
        if intent == AgentIntent.GET_ORDER:
            # data is typically OMSRecord
            message = f"Here are the details for order {data.order_number}."
            spoken = f"Order {data.order_number} is currently {data.status} and is assigned to {data.client_name}."
            return message, spoken
            
        if intent == AgentIntent.LIST_TASKS:
            message = f"I found {data.total} tasks."
            return message, message
            
        if intent == AgentIntent.GET_ORDER_TASKS:
            message = f"I found {len(data)} tasks for that order."
            return message, message
            
        if intent == AgentIntent.LIST_CUSTOMERS:
            message = f"I found {data.total} customers matching your criteria."
            return message, message
            
        if intent == AgentIntent.GET_OVERVIEW:
            message = "Here is the executive overview."
            return message, message
            
        if intent == AgentIntent.GET_ANALYTICS:
            message = "Here is the analytical distribution."
            return message, message
            
        if intent == AgentIntent.CONFIRM_ACTION and isinstance(data, dict):
            # Format WriteService results
            success_count = len(data.get("success", []))
            fail_count = len(data.get("failed", []))
            if fail_count == 0 and success_count == 1:
                message = "Update applied successfully."
                return message, message
            elif fail_count == 0 and success_count > 1:
                message = f"{success_count} orders updated successfully."
                return message, message
            elif success_count > 0 and fail_count > 0:
                message = f"{success_count} orders updated successfully. {fail_count} could not be updated."
                return message, message
            elif success_count == 0 and fail_count > 0:
                message = f"Update failed for {fail_count} orders."
                return message, message
            
        return "Command executed successfully.", "Command executed successfully."

    @staticmethod
    def format_error(error_msg: str) -> Tuple[str, str]:
        return f"Sorry, I encountered an error: {error_msg}", f"Sorry, I encountered an error: {error_msg}"
        
    @staticmethod
    def format_not_found(entity_id: str) -> Tuple[str, str]:
        message = f"I could not find the record: {entity_id}"
        return message, message
