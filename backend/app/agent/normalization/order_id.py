import re

def normalize_order_id(raw_id: str) -> str:
    """
    Normalizes a natural language order ID reference into a canonical OMS order ID.
    Examples:
    "order 612" -> "OR612"
    "order no 612" -> "OR612"
    "OR 612" -> "OR612"
    "O R 6 1 2" -> "OR612"
    "OR612" -> "OR612"
    """
    if not raw_id:
        return raw_id
        
    # Remove all spaces, hyphens, and periods
    cleaned = re.sub(r'[\s\-\.]', '', raw_id.lower())
    
    # Strip common conversational prefixes
    # "ordernumber", "orderno", "order"
    if cleaned.startswith("ordernumber"):
        cleaned = cleaned[11:]
    elif cleaned.startswith("orderno"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("order"):
        cleaned = cleaned[5:]
        
    # If the remaining string is just digits, prepend "or"
    if cleaned.isdigit():
        cleaned = f"or{cleaned}"
        
    return cleaned.upper()
