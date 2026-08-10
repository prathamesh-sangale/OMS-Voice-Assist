class AuthorizationService:
    """
    Mock authorization boundary.
    In a real app, this checks the JWT/RBAC of the caller.
    Here, we assume the actor is the CEO and is authorized.
    """
    def __init__(self):
        self._actor = "CEO"

    def authorize(self, intent: str, target: str) -> bool:
        # The CEO can authorize anything in Phase 5
        return True
