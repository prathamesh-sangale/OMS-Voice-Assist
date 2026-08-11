from typing import Optional
from .models import ConversationSession, SessionMessage
from .repository import SessionRepository

class SessionService:
    def __init__(self, repository: SessionRepository):
        self._repo = repository

    def get_or_create_session(self, session_id: Optional[str] = None) -> ConversationSession:
        if session_id:
            session = self._repo.get_session(session_id)
            if session:
                return session
        
        # Create new
        new_session = ConversationSession()
        self._repo.save_session(new_session)
        return new_session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        return self._repo.get_session(session_id)

    def save_session(self, session: ConversationSession):
        self._repo.save_session(session)

    def process_pending_answer(self, session: ConversationSession, user_input: str) -> bool:
        """
        If the session is waiting for a specific field, directly assign the user input to it
        and clear the pending state. Returns True if an answer was processed.
        """
        if session.context.operation_status == "collecting" and session.context.pending_field:
            field = session.context.pending_field
            
            clean_input = user_input.strip().lower()
            if clean_input in ["cancel", "abort", "stop"]:
                session.context.pending_field = None
                session.context.operation_status = "idle"
                session.context.draft = {}
                self.save_session(session)
                return True
                
            # Direct assignment. A more advanced version might parse the type (e.g. integer for quantity)
            # but string is safe for the UI draft. DraftManager will validate it.
            session.context.draft[field] = user_input.strip()
            session.context.pending_field = None
            self.save_session(session)
            return True
        return False
