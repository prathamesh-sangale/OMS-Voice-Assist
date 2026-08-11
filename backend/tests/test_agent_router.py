from unittest.mock import Mock, MagicMock
import pytest
from app.agent.router import AgentRouter
from app.agent.models.command import CommandInput, IntentResult
from app.agent.models.intent import AgentIntent
from app.agent.sessions.session_service import SessionService
from app.agent.resolution.target_resolver import TargetResolverService

@pytest.fixture
def mock_session_service():
    mock = MagicMock(spec=SessionService)
    # Stub get_or_create_session to return a session with a title
    session = MagicMock()
    session.id = "mock-session-123"
    session.title = "New Conversation"
    session.messages = []
    session.context = MagicMock()
    session.context.operation_status = None
    mock.get_or_create_session.return_value = session
    mock.process_pending_answer.return_value = False
    return mock

@pytest.fixture
def mock_target_resolver():
    mock = MagicMock(spec=TargetResolverService)
    # Default return
    target = MagicMock()
    target.is_ambiguous = False
    mock.resolve_target.return_value = target
    return mock

@pytest.fixture
def mock_analyzer():
    return Mock()

@pytest.fixture
def mock_executor():
    return Mock()

def test_router_handles_unsupported(mock_analyzer, mock_executor, mock_session_service, mock_target_resolver):
    mock_analyzer.analyze.return_value = IntentResult(
        intent=AgentIntent.UNSUPPORTED,
        confidence=1.0
    )
    router = AgentRouter(mock_analyzer, mock_executor, mock_session_service, mock_target_resolver)
    res = router.handle_command(CommandInput(text="delete something"))
    
    assert res.status == "unsupported"
    assert "I can't perform that OMS operation yet." in res.message
    mock_executor.execute.assert_not_called()

def test_router_handles_clarification(mock_analyzer, mock_executor, mock_session_service, mock_target_resolver):
    mock_analyzer.analyze.return_value = IntentResult(
        intent=AgentIntent.NEEDS_CLARIFICATION,
        confidence=1.0
    )
    router = AgentRouter(mock_analyzer, mock_executor, mock_session_service, mock_target_resolver)
    res = router.handle_command(CommandInput(text="show the order"))
    
    assert res.status == "needs_clarification"
    assert res.requires_clarification is True
    mock_executor.execute.assert_not_called()

def test_router_executes_successfully(mock_analyzer, mock_executor, mock_session_service, mock_target_resolver):
    mock_analyzer.analyze.return_value = IntentResult(
        intent=AgentIntent.GET_ANALYTICS,
        confidence=0.9
    )
    mock_executor.execute.return_value = {"fake": "data"}
    
    router = AgentRouter(mock_analyzer, mock_executor, mock_session_service, mock_target_resolver)
    res = router.handle_command(CommandInput(text="show analytics"))
    
    assert res.status == "success"
    assert res.data == {"fake": "data"}
    mock_executor.execute.assert_called_once()
