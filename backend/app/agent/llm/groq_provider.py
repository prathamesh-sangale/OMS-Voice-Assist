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
        from .prompts import AGENT_SYSTEM_PROMPT
        from datetime import datetime
        system_prompt = AGENT_SYSTEM_PROMPT
        system_prompt += f"\nToday's Date is: {datetime.now().strftime('%Y-%m-%d')}\n"
        if session_context:            
            from datetime import datetime
            current_date = datetime.now().strftime('%d %B %Y')
            system_prompt += f"\nActive Session Context: {json.dumps(session_context)}\n"
            system_prompt += f"\nCurrent Date: {current_date}\n"
        
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
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1]
                
            print(f"RAW LLM RESPONSE: {result_text}")
            data = json.loads(result_text)
            
            intent_str = data.get("intent", AgentIntent.UNSUPPORTED.value)
            if isinstance(intent_str, str) and intent_str.startswith("AgentIntent."):
                intent_str = intent_str.replace("AgentIntent.", "")
            
            return LLMStructuredIntent(
                intent=intent_str,
                confidence=float(data.get("confidence", 0.0)),
                entities=data.get("entities", {}),
                explanation=data.get("explanation", "AI analyzed via Groq.")
            )
        except Exception as e:
            logger.error(f"Groq LLM Error: {e}")
            raise LLMUnavailableError(f"Failed to parse command with Groq: {e}")
