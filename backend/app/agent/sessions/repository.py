import json
import os
import threading
from typing import Dict, List, Optional
from .models import ConversationSession

class SessionRepository:
    """
    JSON file-based repository for storing conversation sessions.
    Mirrors the OMS JSONRepository architecture for thread safety and persistence.
    """
    def __init__(self, data_file: str = "app/data/sessions.json"):
        self.data_file = data_file
        self._lock = threading.RLock()
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump({}, f)
                
    def _read_data(self) -> Dict[str, dict]:
        with self._lock:
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}

    def _write_data(self, data: Dict[str, dict]):
        with self._lock:
            tmp_file = self.data_file + ".tmp"
            with open(tmp_file, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_file, self.data_file)

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        data = self._read_data()
        if session_id in data:
            return ConversationSession(**data[session_id])
        return None

    def save_session(self, session: ConversationSession):
        data = self._read_data()
        data[session.id] = session.model_dump()
        self._write_data(data)

    def list_sessions(self, limit: int = 50) -> List[ConversationSession]:
        data = self._read_data()
        sessions = [ConversationSession(**s) for s in data.values()]
        sessions.sort(key=lambda x: x.updated_at, reverse=True)
        return sessions[:limit]
