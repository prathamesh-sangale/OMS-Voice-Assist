from app.agent.analyzer import RuleEngineAnalyzer
from app.agent.resolution.entity_resolver import ResolutionResult
from unittest.mock import Mock
from app.agent.models.command import CommandInput
from app.agent.models.intent import AgentIntent

def get_analyzer():
    mock_resolver = Mock()
    mock_resolver.resolve_sales_exec.return_value = ResolutionResult(resolved_value="Rohit Menon")
    return RuleEngineAnalyzer(mock_resolver)

def test_analyzer_show_pending_orders():
    analyzer = get_analyzer()
    res = analyzer.analyze(CommandInput(text="show pending orders"))
    assert res.intent == AgentIntent.LIST_ORDERS
    assert res.entities.get("status") == "pending"

def test_analyzer_show_order_specific():
    analyzer = get_analyzer()
    res = analyzer.analyze(CommandInput(text="show order OR615"))
    assert res.intent == AgentIntent.GET_ORDER
    assert res.entities.get("order_id") == "OR615"

def test_analyzer_show_tasks_specific():
    analyzer = get_analyzer()
    res = analyzer.analyze(CommandInput(text="show tasks for OR615"))
    assert res.intent == AgentIntent.GET_ORDER_TASKS
    assert res.entities.get("order_id") == "OR615"

def test_analyzer_show_analytics():
    analyzer = get_analyzer()
    res = analyzer.analyze(CommandInput(text="show analytics"))
    assert res.intent == AgentIntent.GET_ANALYTICS

def test_analyzer_clarification():
    analyzer = get_analyzer()
    res = analyzer.analyze(CommandInput(text="show the order"))
    assert res.intent == AgentIntent.NEEDS_CLARIFICATION

def test_analyzer_unsupported_write():
    analyzer = get_analyzer()
    res = analyzer.analyze(CommandInput(text="delete order OR615"))
    assert res.intent == AgentIntent.UNSUPPORTED
