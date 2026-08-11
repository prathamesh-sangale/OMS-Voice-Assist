from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class SessionMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str = Field(description="'user' or 'agent'")
    text: str = Field(description="The message text")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    input_mode: Optional[str] = Field(default=None, description="text or voice (if user)")
    response_type: Optional[str] = Field(default=None, description="Type of response card")
    data: Optional[Any] = Field(default=None, description="Structured data for the card")

class SessionContext(BaseModel):
    intent: Optional[str] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    pending_field: Optional[str] = None
    draft: Dict[str, Any] = Field(default_factory=dict)
    operation_status: str = Field(default="idle", description="idle, collecting, pending_confirmation, executed")
    confirmation_id: Optional[str] = None
    last_result_context: Dict[str, Any] = Field(default_factory=dict, description="Stores query, filters, and identifiers from last read")
    target_orders: Optional[Dict[str, Any]] = Field(default=None, description="Structured target set: {type: str, order_ids: List[str], source: str, query_context: dict}")

class ConversationSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(default="New Conversation")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    messages: List[SessionMessage] = Field(default_factory=list)
    context: SessionContext = Field(default_factory=SessionContext)
    
    def add_message(self, role: str, text: str, input_mode: Optional[str] = None, response_type: Optional[str] = None, data: Optional[Any] = None):
        self.messages.append(SessionMessage(role=role, text=text, input_mode=input_mode, response_type=response_type, data=data))
        self.updated_at = datetime.utcnow().isoformat()
