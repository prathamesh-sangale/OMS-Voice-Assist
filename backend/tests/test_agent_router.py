from unittest.mock import Mock
import pytest
from app.agent.router import AgentRouter
from app.agent.models.command import CommandInput, IntentResult
from app.agent.models.intent import AgentIntent

@pytest.fixture
def mock_analyzer():
    return Mock()

@pytest.fixture
def mock_executor():
    return Mock()

def test_router_handles_unsupported(mock_analyzer, mock_executor):
    mock_analyzer.analyze.return_value = IntentResult(
        intent=AgentIntent.UNSUPPORTED,
        confidence=1.0
    )
    router = AgentRouter(mock_analyzer, mock_executor)
    res = router.handle_command(CommandInput(text="delete something"))
    
    assert res.status == "unsupported"
    assert "Write operations are disabled" in res.message
    mock_executor.execute.assert_not_called()

def test_router_handles_clarification(mock_analyzer, mock_executor):
    mock_analyzer.analyze.return_value = IntentResult(
        intent=AgentIntent.NEEDS_CLARIFICATION,
        confidence=1.0
    )
    router = AgentRouter(mock_analyzer, mock_executor)
    res = router.handle_command(CommandInput(text="show the order"))
    
    assert res.status == "needs_clarification"
    assert res.requires_clarification is True
    mock_executor.execute.assert_not_called()

def test_router_executes_successfully(mock_analyzer, mock_executor):
    mock_analyzer.analyze.return_value = IntentResult(
        intent=AgentIntent.GET_ANALYTICS,
        confidence=0.9
    )
    mock_executor.execute.return_value = {"fake": "data"}
    
    router = AgentRouter(mock_analyzer, mock_executor)
    res = router.handle_command(CommandInput(text="show analytics"))
    
    assert res.status == "success"
    assert res.data == {"fake": "data"}
    mock_executor.execute.assert_called_once()
