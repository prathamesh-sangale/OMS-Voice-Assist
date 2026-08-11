import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel

class PendingAction(BaseModel):
    id: str
    intent: str
    command_payload: Dict[str, Any]
    description: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    target: Any
    expires_at: datetime

class ConfirmationService:
    """
    Manages short-lived server-side state for pending write actions.
    """
    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, PendingAction] = {}
        self._ttl = ttl_seconds

    def create_pending_action(
        self, 
        intent: str, 
        command_payload: Dict[str, Any], 
        description: str,
        target: Any,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None
    ) -> PendingAction:
        action_id = str(uuid.uuid4())
        action = PendingAction(
            id=action_id,
            intent=intent,
            command_payload=command_payload,
            description=description,
            target=target,
            old_value=old_value,
            new_value=new_value,
            expires_at=datetime.utcnow() + timedelta(seconds=self._ttl)
        )
        self._cache[action_id] = action
        return action

    def get_and_validate(self, action_id: str) -> Optional[PendingAction]:
        action = self._cache.get(action_id)
        if not action:
            return None
        
        if datetime.utcnow() > action.expires_at:
            del self._cache[action_id]
            return None
            
        return action

    def consume(self, action_id: str) -> None:
        """Removes the action after execution."""
        if action_id in self._cache:
            del self._cache[action_id]
