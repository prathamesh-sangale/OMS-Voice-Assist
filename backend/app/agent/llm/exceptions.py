class LLMException(Exception):
    """Base exception for LLM errors."""
    pass

class LLMUnavailableError(LLMException):
    """Raised when the LLM service cannot be reached."""
    pass

class LLMValidationError(LLMException):
    """Raised when the LLM returns unstructured or invalid data."""
    pass
