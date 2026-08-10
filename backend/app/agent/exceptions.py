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
    """Raised when an operation fails during execution."""
    pass

class AuthorizationError(AgentException):
    """Raised when the actor is not authorized to perform the action."""
    pass

class ConfirmationRequiredError(AgentException):
    """Raised when an action requires explicit confirmation before executing."""
    def __init__(self, pending_action_id: str, action_details: dict):
        self.pending_action_id = pending_action_id
        self.action_details = action_details
        super().__init__("Confirmation required.")
