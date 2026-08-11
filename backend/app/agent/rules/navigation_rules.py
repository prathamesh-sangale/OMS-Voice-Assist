from typing import Optional
import re
from .base import CommandRule
from ..models.command import IntentResult
from ..models.intent import AgentIntent

class NavigationRule(CommandRule):
    """
    Handles explicit navigation commands.
    Examples: "Open Dashboard", "Go to Orders", "Take me to Tasks", "Navigate to Analytics"
    """
    
    name: str = "navigation_rule"
    intent: AgentIntent = AgentIntent.UNSUPPORTED
    priority: int = 100
    
    def __init__(self):
        self.nav_patterns = [
            r"open\s+(.+)",
            r"go\s+to\s+(.+)",
            r"take\s+me\s+to\s+(.+)",
            r"navigate\s+to\s+(.+)",
            r"show\s+me\s+(?:the\s+)?(.+?)\s+page",
        ]
        
        self.targets = {
            "dashboard": AgentIntent.NAVIGATE_TO_DASHBOARD,
            "home": AgentIntent.NAVIGATE_TO_DASHBOARD,
            "overview": AgentIntent.NAVIGATE_TO_DASHBOARD,
            
            "orders": AgentIntent.NAVIGATE_TO_ORDERS,
            "order list": AgentIntent.NAVIGATE_TO_ORDERS,
            
            "tasks": AgentIntent.NAVIGATE_TO_TASKS,
            "task list": AgentIntent.NAVIGATE_TO_TASKS,
            
            "analytics": AgentIntent.NAVIGATE_TO_ANALYTICS,
            "stats": AgentIntent.NAVIGATE_TO_ANALYTICS,
            "statistics": AgentIntent.NAVIGATE_TO_ANALYTICS,
            
            "customers": AgentIntent.NAVIGATE_TO_CUSTOMERS,
            "clients": AgentIntent.NAVIGATE_TO_CUSTOMERS,
            
            "voice command center": AgentIntent.NAVIGATE_TO_COMMAND_CENTER,
            "command center": AgentIntent.NAVIGATE_TO_COMMAND_CENTER,
            "voice center": AgentIntent.NAVIGATE_TO_COMMAND_CENTER,
            "chat": AgentIntent.NAVIGATE_TO_COMMAND_CENTER
        }

    def match(self, text: str) -> Optional[IntentResult]:
        # Simple combined command check: "Open Orders and show pending"
        # We only handle the first part for pure navigation, or the parser handles it.
        # For this rule, we just check if it's purely a navigation command, 
        # or if it starts with a navigation command.
        
        # We will parse pure navigation here. If there is an "and", we might leave it to the LLM or handle it as a query.
        if " and " in text:
            # Let the LLM or other rules handle combined commands, unless we want to split them here.
            # But the prompt says we should support "NAVIGATE_TO_ORDERS + LIST_ORDERS"
            # Actually, the Router can just return a navigation hint automatically for LIST_ORDERS.
            pass
            
        text_lower = text.lower().strip()
        
        for pattern in self.nav_patterns:
            match = re.match(pattern, text_lower)
            if match:
                target_str = match.group(1).strip()
                # Remove punctuation
                target_str = re.sub(r'[^\w\s]', '', target_str)
                
                # If target is exact
                if target_str in self.targets:
                    return IntentResult(
                        intent=self.targets[target_str],
                        confidence=0.9,
                        explanation=f"Matched explicit navigation to {target_str}"
                    )
                    
                # Substring match
                for key, intent in self.targets.items():
                    if key in target_str:
                        return IntentResult(
                            intent=intent,
                            confidence=0.8,
                            explanation=f"Matched navigation target containing '{key}'"
                        )
                        
        return None
