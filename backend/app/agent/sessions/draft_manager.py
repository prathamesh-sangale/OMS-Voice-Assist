from typing import Dict, Any, Optional, Tuple
from ..models.intent import AgentIntent

class DraftManager:
    """
    Manages structured drafts and determines missing required fields based on intents.
    """
    ALLOWED_STATUSES = ["pending", "in progress", "needs revision", "shipped", "delivered", "canceled", "completed", "active", "approved"]
    
    REQUIRED_FIELDS = {
        AgentIntent.CREATE_ORDER.value: [
            "client_name",
            "product_type",
            "business_model",
            "quantity",
            "loading_city",
            "delivery_city",
            "commitment_date"
        ],
        AgentIntent.UPDATE_ORDER_STATUS.value: [
            "new_status"
        ],
        AgentIntent.UPDATE_COMMITMENT_DATE.value: [
            "new_commitment_date"
        ],
        AgentIntent.UPDATE_ORDER_DESTINATION.value: [
            "new_destination"
        ]
    }
    
    FIELD_PROMPTS = {
        "client_name": "What is the name of the client?",
        "product_type": "What type of product is this order for?",
        "business_model": "What is the business model (e.g., Sale, Rental, Lease)?",
        "quantity": "What is the quantity?",
        "loading_city": "Which city will the items be loaded from?",
        "delivery_city": "What is the delivery city?",
        "commitment_date": "What is the commitment date for this order?",
        "new_status": "What status should I update this to?",
        "new_commitment_date": "What is the new commitment date?",
        "new_destination": "What should the new destination be?"
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
            if field == "new_status":
                if str(val).lower() not in cls.ALLOWED_STATUSES:
                    # Invalidate the field
                    draft[field] = None
                    return False, field, "Please provide a valid status, or say cancel."
            
            if field == "new_destination":
                if not isinstance(val, str) or len(val.strip()) < 2 or val.lower() in ["nothing", "none", "null", "empty"]:
                    draft[field] = None
                    return False, field, "Please provide a valid destination, or say cancel."
                    
            if field == "new_commitment_date":
                if not isinstance(val, str) or len(val.strip()) < 5 or val.lower() in ["nothing", "none", "null", "empty"]:
                    draft[field] = None
                    return False, field, "Please provide a valid date, or say cancel."

        return True, None, None
