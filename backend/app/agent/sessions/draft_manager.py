from typing import Dict, Any, Optional, Tuple
from ..models.intent import AgentIntent

class DraftManager:
    """
    Manages structured drafts and determines missing required fields based on intents.
    """
    ALLOWED_STATUSES = ["pending", "in progress", "needs revision", "shipped", "delivered", "canceled", "cancelled", "completed", "active", "approved"]
    
    REQUIRED_FIELDS = {
        AgentIntent.CREATE_ORDER.value: [
            "client_name",
            "product_type",
            "quantity",
            "loading_city",
            "delivery_city",
            "commitment_date"
        ],
        AgentIntent.UPDATE_ORDER.value: [
            "updates"
        ]
    }
    
    FIELD_PROMPTS = {
        "client_name": "What is the name of the client?",
        "product_type": "What container type is needed (e.g., Dry, Reefer)?",
        "quantity": "What is the quantity?",
        "loading_city": "What is the pickup city?",
        "delivery_city": "What is the destination city?",
        "commitment_date": "What is the commitment date for this order?",
        "updates": "What would you like to update on this order?"
    }

    @classmethod
    def evaluate_draft(cls, intent: str, draft: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Evaluates the draft for the given intent.
        Returns: (is_complete, missing_field_key, missing_field_prompt)
        """
        required = cls.REQUIRED_FIELDS.get(intent, [])
        for field in required:
            val = draft.get(field)
            if not val:
                prompt = cls.FIELD_PROMPTS.get(field, f"Please provide the {field}.")
                return False, field, prompt
                
            # Strict Validation Rules
            if field == "updates":
                if not isinstance(val, dict) or not val:
                    # Invalidate if it's not a valid dict
                    draft[field] = None
                    return False, field, "Please specify what you would like to update."
                
                # Check for status validation inside updates
                if "status" in val:
                    if str(val["status"]).lower() not in cls.ALLOWED_STATUSES:
                        draft[field] = None
                        return False, field, "Please provide a valid status, or say cancel."

        return True, None, None
