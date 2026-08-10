from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from .intent import AgentIntent

class CommandInput(BaseModel):
    text: str = Field(description="The natural language command from the user")
    source: str = Field(default="text", description="Source of the command (e.g. text, voice)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context if needed")

class IntentResult(BaseModel):
    intent: AgentIntent
    confidence: float = Field(ge=0.0, le=1.0)
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    query: Optional[Any] = Field(default=None, description="The strictly typed query contract to be passed to OMS")
    explanation: Optional[str] = Field(default=None, description="Explanation of how the intent was resolved")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata such as resolution method")

class AgentResponse(BaseModel):
    status: str = Field(description="success, needs_clarification, unsupported, error")
    message: str = Field(description="Human readable response text")
    intent: Optional[AgentIntent] = Field(default=None)
    data: Optional[Any] = Field(default=None, description="Payload returned by OMS")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Audit log context")
    requires_clarification: bool = Field(default=False)
