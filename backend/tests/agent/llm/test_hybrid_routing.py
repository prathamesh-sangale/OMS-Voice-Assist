from unittest.mock import Mock
from app.agent.analyzer import HybridAnalyzer
from app.agent.llm.mock_provider import FakeLLMProvider
from app.agent.resolution.entity_resolver import ResolutionResult
from app.agent.models.command import CommandInput
from app.agent.models.intent import AgentIntent

def get_hybrid_analyzer(fail_mode=False):
    mock_resolver = Mock()
    # Need to properly mock resolution for LIST_ORDERS with sales_exec
    mock_resolver.resolve_sales_exec.return_value = ResolutionResult(resolved_value="Rohit Menon")
    llm = FakeLLMProvider(fail_mode=fail_mode)
    return HybridAnalyzer(mock_resolver, llm)

def test_hybrid_routing_rule_match():
    # Simple query should not hit LLM
    analyzer = get_hybrid_analyzer()
    res = analyzer.analyze(CommandInput(text="show orders"))
    assert res.intent == AgentIntent.LIST_ORDERS
    assert res.metadata.get("method") == "Rule Engine"

def test_hybrid_routing_llm_fallback():
    # Complex query should fallback to LLM
    analyzer = get_hybrid_analyzer()
    res = analyzer.analyze(CommandInput(text="which orders need my attention?"))
    assert res.intent == AgentIntent.LIST_ORDERS
    assert res.metadata.get("method") == "AI"
    assert res.entities.get("status") == "pending"

def test_hybrid_routing_llm_failure():
    # If LLM fails, return graceful UNSUPPORTED
    analyzer = get_hybrid_analyzer(fail_mode=True)
    res = analyzer.analyze(CommandInput(text="which orders need my attention?"))
    assert res.intent == AgentIntent.UNSUPPORTED
    assert "unavailable" in res.explanation
    assert res.metadata.get("method") == "AI Fallback Error"

def test_hybrid_routing_security_ban():
    # Banned words should stop before LLM
    analyzer = get_hybrid_analyzer()
    res = analyzer.analyze(CommandInput(text="delete orders that need my attention"))
    assert res.intent == AgentIntent.UNSUPPORTED
    assert res.metadata.get("method") == "Security Policy"
