import re
import logging

logger = logging.getLogger(__name__)

class AudioNormalizer:
    """
    Normalizes transcript text to ensure OMS domain terminology is correct before hitting the Agent.
    """
    @staticmethod
    def normalize(text: str) -> str:
        original = text
        # Example: "order O R six zero three" -> "order OR603"
        # Since Whisper is usually smart, it might output "OR 603" or "O R 603"
        
        # Replace spaced out O R
        text = re.sub(r'\bo\s*r\s*(\d{3})\b', r'OR\1', text, flags=re.IGNORECASE)
        
        # Replace "O R" followed by spelled out numbers (naive approach for a few common ones)
        # Note: Whisper turbo handles numbers well, but this is a safety net.
        number_words = {
            "six": "6",
            "zero": "0",
            "three": "3",
            "one": "1",
            "two": "2",
            "four": "4",
            "five": "5",
            "seven": "7",
            "eight": "8",
            "nine": "9",
        }
        
        # Normalize "O R six zero three"
        # A more robust regex/replace for basic OMS commands:
        if "o r " in text.lower():
            for word, digit in number_words.items():
                text = re.sub(rf'\b{word}\b', digit, text, flags=re.IGNORECASE)
            
            text = text.replace(" ", "")
            text = text.replace("or", "OR")
            
        # Reverting overly aggressive space removal if needed, but for our simple demo, 
        # a safer regex for just the ORXXX pattern:
        
        # Let's just use a focused regex for "O R [0-9]+" or "OR [0-9]+"
        text = original
        text = re.sub(r'\b(?:O\s*R|or)\s*(\d+)\b', r'OR\1', text, flags=re.IGNORECASE)
        
        # Also clean up trailing punctuation that might confuse exact matches
        text = text.strip()
        
        if text != original:
            logger.debug(f"Normalized transcript from '{original}' to '{text}'")
            
        return text
