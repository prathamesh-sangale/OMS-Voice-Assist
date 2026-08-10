import pytest
from unittest.mock import Mock
from app.agent.execution.executor import AgentExecutor
from app.agent.models.intent import AgentIntent
from app.agent.models.command import IntentResult
from app.agent.exceptions import UnsupportedIntentError
from app.oms.exceptions import OMSRecordNotFoundError

@pytest.fixture
def mock_oms():
    return Mock()

def test_executor_successful_mapping(mock_oms):
    mock_oms.get_overview_metrics.return_value = "metrics_data"
    
    executor = AgentExecutor(mock_oms, Mock(), Mock())
    res = executor.execute(IntentResult(
        intent=AgentIntent.GET_OVERVIEW,
        confidence=1.0
    ))
    
    assert res == "metrics_data"
    mock_oms.get_overview_metrics.assert_called_once()

def test_executor_denies_unregistered_intent(mock_oms):
    executor = AgentExecutor(mock_oms, Mock(), Mock())
    with pytest.raises(UnsupportedIntentError):
        executor.execute(IntentResult(
            intent=AgentIntent.UNSUPPORTED,
            confidence=1.0
        ))

def test_executor_raises_not_found(mock_oms):
    mock_oms.retrieve_order_details.side_effect = OMSRecordNotFoundError("Not found")
    executor = AgentExecutor(mock_oms, Mock(), Mock())
    
    with pytest.raises(OMSRecordNotFoundError):
        executor.execute(IntentResult(
            intent=AgentIntent.GET_ORDER,
            confidence=1.0,
            query="OR999999"
        ))
