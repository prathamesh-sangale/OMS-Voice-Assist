class AgentException(Exception):
    """Base class for agent exceptions."""
    pass

class AgentValidationError(AgentException):
    """Raised when an intent result fails security or schema validation."""
    pass

class UnsupportedIntentError(AgentException):
    """Raised when an intent is explicitly unsupported."""
    pass

class ExecutionError(AgentException):
    """Raised when the capability registry fails to execute the command against the OMS."""
    pass
