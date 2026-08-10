from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from ..models.intent import AgentIntent

class LLMStructuredIntent(BaseModel):
    intent: AgentIntent = Field(description="The mapped AgentIntent from the command.")
    confidence: float = Field(description="Confidence score between 0 and 1.")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities like status, order_id, sales_exec_candidate, business_model.")
    explanation: str = Field(description="Concise summary of the reasoning.")
