import logging
import json
from datetime import datetime, timezone
from typing import Any, Optional
from app.core.context import request_id_var

logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Records audit events for OMS write operations.
    """
    def __init__(self, log_file: str = "app/data/audit.log"):
        self.log_file = log_file

    def log_event(
        self,
        actor: str,
        intent: str,
        target: str,
        old_value: Optional[Any],
        new_value: Optional[Any],
        status: str,
        reason: Optional[str] = None
    ):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id_var.get(),
            "actor": actor,
            "intent": intent,
            "target": target,
            "old_value": old_value,
            "new_value": new_value,
            "status": status,
            "reason": reason
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Failed to write to audit log: {e}")
