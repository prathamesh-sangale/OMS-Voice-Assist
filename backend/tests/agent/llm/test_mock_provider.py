import pytest
from app.agent.llm.mock_provider import FakeLLMProvider
from app.agent.llm.exceptions import LLMUnavailableError
from app.agent.models.intent import AgentIntent

def test_mock_provider_success():
    provider = FakeLLMProvider()
    res = provider.parse_command("which orders need my attention?")
    assert res.intent == AgentIntent.LIST_ORDERS
    assert res.entities.get("status") == "pending"

def test_mock_provider_clarification():
    provider = FakeLLMProvider()
    res = provider.parse_command("this command has a missing entity")
    assert res.intent == AgentIntent.NEEDS_CLARIFICATION

def test_mock_provider_unsupported():
    provider = FakeLLMProvider()
    res = provider.parse_command("something completely random that it does not understand")
    assert res.intent == AgentIntent.UNSUPPORTED

def test_mock_provider_failure():
    provider = FakeLLMProvider(fail_mode=True)
    with pytest.raises(LLMUnavailableError):
        provider.parse_command("any text")
