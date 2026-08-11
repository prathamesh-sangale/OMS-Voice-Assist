import json
import logging
from groq import Groq
from .provider import LLMProvider
from .schemas import LLMStructuredIntent
from ..models.intent import AgentIntent
from .exceptions import LLMUnavailableError
import os

logger = logging.getLogger(__name__)

class GroqLLMProvider(LLMProvider):
    """
    Real LLM Provider using Groq's whisper-large-v3-turbo (wait, LLMs don't use whisper, they use llama-3.1-70b-versatile or similar).
    We will use llama3-8b-8192 or llama3-70b-8192.
    """
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be set to use GroqLLMProvider")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-8b-instant"
        
    def parse_command(self, text: str, session_context: dict = None) -> LLMStructuredIntent:
        system_prompt = """
        You are the CEO Executive OMS Agent. 
        Your task is to classify the user's intent into one of the following capabilities:
        GET_ORDER, LIST_ORDERS, GET_ORDER_TASKS, LIST_TASKS, LIST_CUSTOMERS, GET_OVERVIEW, GET_ANALYTICS, UPDATE_ORDER_STATUS, UPDATE_COMMITMENT_DATE, UPDATE_ORDER_DESTINATION, UNSUPPORTED.
        
        Extract relevant entities for filtering or targeting (e.g. order_id like OR601, status, business_model, product, search, department, stage).
        
        CRITICAL: Conversational Refinements
        If the user provides a refinement or correction (e.g., "quantity 2", "make it Mumbai", "not reefer"), you MUST merge these new constraints with the Active Query Context provided below. If they negate a filter, replace it. If they add a filter, include it with the existing ones. Do not discard previous filters unless instructed.
        
        Return ONLY valid JSON matching this schema:
        {
            "intent": "<intent_name>",
            "confidence": <float 0.0-1.0>,
            "entities": {"key": "value"},
            "explanation": "<short explanation>"
        }
        """
        
        if session_context:
            system_prompt += f"\nActive Query Context: {json.dumps(session_context)}\n"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            data = json.loads(result_text)
            
            return LLMStructuredIntent(
                intent=data.get("intent", AgentIntent.UNSUPPORTED.value),
                confidence=float(data.get("confidence", 0.0)),
                entities=data.get("entities", {}),
                explanation=data.get("explanation", "AI analyzed via Groq.")
            )
        except Exception as e:
            logger.error(f"Groq LLM Error: {e}")
            raise LLMUnavailableError(f"Failed to parse command with Groq: {e}")
