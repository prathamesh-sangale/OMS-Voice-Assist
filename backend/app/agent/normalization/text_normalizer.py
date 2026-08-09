import re

class TextNormalizer:
    """
    Normalizes command strings for the Rule Engine.
    Preserves identifiers (like OR615) while standardizing spaces, case, and punctuation.
    """
    
    @staticmethod
    def normalize(text: str) -> str:
        if not text:
            return ""
            
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # We lowercase for simpler pattern matching in rules
        text = text.lower()
        
        # Remove common punctuation but preserve hyphens/alphanumerics that might be part of IDs
        # e.g., "pending," -> "pending"
        text = re.sub(r'[.,;!?"\']', ' ', text)
        
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
