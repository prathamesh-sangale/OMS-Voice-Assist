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
            "order_type",
            "product_type",
            "quantity",
            "loading_city",
            "delivery_city",
            "commitment_date",
            "business_model"
        ],
        AgentIntent.UPDATE_ORDER.value: [
            "updates"
        ]
    }
    
    FIELD_PROMPTS = {
        "client_name": "What is the name of the client?",
        "order_type": "What is the order type (e.g., rental, sale, lease)?",
        "product_type": "What container type is needed (e.g., Dry, Reefer)?",
        "quantity": "What is the quantity?",
        "loading_city": "What is the pickup city?",
        "delivery_city": "What is the destination city?",
        "commitment_date": "What is the commitment date for this order?",
        "business_model": "What is the business model?",
        "updates": "What would you like to update on this order?"
    }

    @classmethod
    def _validate_commitment_date(cls, val: Any) -> Tuple[bool, str, Any]:
        from datetime import datetime
        import dateparser
        
        dt = dateparser.parse(
            str(val).lower().replace('next ', ''), 
            settings={'PREFER_DATES_FROM': 'future'}
        )
        if not dt:
            return False, "That doesn't seem like a valid date format. Please specify the commitment date again.", val
            
        if dt.date() < datetime.now().date():
            return False, "The commitment date cannot be in the past. Please provide today's date or a future date.", val
            
        formatted_date = dt.strftime("%d-%m-%Y")
        return True, "", formatted_date

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
                        
                if "commitment_date" in val:
                    is_valid, err_msg, parsed_date = cls._validate_commitment_date(val["commitment_date"])
                    if not is_valid:
                        # Clear it from the updates dict so the user is reprompted
                        del draft[field]["commitment_date"]
                        if not draft[field]:
                            draft[field] = None
                        return False, field, err_msg
                    else:
                        draft[field]["commitment_date"] = parsed_date
                        
            if field == "commitment_date":
                is_valid, err_msg, parsed_date = cls._validate_commitment_date(val)
                if not is_valid:
                    draft[field] = None
                    return False, field, err_msg
                else:
                    draft[field] = parsed_date

        return True, None, None
