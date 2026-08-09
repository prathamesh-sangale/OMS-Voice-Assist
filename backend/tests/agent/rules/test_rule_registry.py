from app.agent.rules.registry import RuleRegistry
from app.agent.rules.order_rules import GetOrderRule, ListOrdersGenericRule
from app.agent.models.intent import AgentIntent

def test_rule_registry_priority():
    registry = RuleRegistry()
    registry.register(ListOrdersGenericRule()) # Priority 80
    registry.register(GetOrderRule()) # Priority 100
    
    # "show order OR123" could theoretically match a sloppy generic list rule 
    # depending on regex, but priority 100 goes first.
    res = registry.evaluate("show order or123")
    assert res.intent == AgentIntent.GET_ORDER
    assert res.entities["order_id"] == "OR123"

def test_rule_registry_unsupported():
    registry = RuleRegistry()
    res = registry.evaluate("some random non matching command")
    assert res.intent == AgentIntent.UNSUPPORTED
