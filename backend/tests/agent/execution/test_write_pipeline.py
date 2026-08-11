import pytest
from unittest.mock import Mock, patch
from app.agent.models.intent import AgentIntent
from app.agent.models.command import IntentResult, CommandInput
from app.agent.exceptions import ConfirmationRequiredError, AuthorizationError
from app.oms.exceptions import OMSRecordNotFoundError
from app.oms.schemas.oms import OrderSchema

@pytest.fixture
def mock_oms():
    oms = Mock()
    # Provide a mock order for OR603
    mock_order = OrderSchema(
        id="OR603",
        order_number="OR603",
        client_name="Test Client",
        status="Pending",
        commitment_date="2026-08-11"
    )
    oms.get_order.return_value = mock_order
    oms.retrieve_order_details.return_value = mock_order
    return oms

@pytest.fixture
def mock_write_service():
    ws = Mock()
    # Return updated mock order
    updated_order = OrderSchema(
        id="OR603",
        order_number="OR603",
        client_name="Test Client",
        status="Shipped",
        commitment_date="2026-08-15"
    )
    ws.update_order_status.return_value = updated_order
    ws.update_commitment_date.return_value = updated_order
    return ws

@pytest.fixture
def confirmation_service():
    from app.agent.execution.confirmation import ConfirmationService
    return ConfirmationService()

@pytest.fixture
def executor(mock_oms, mock_write_service, confirmation_service):
    from app.agent.execution.executor import AgentExecutor
    return AgentExecutor(mock_oms, mock_write_service, confirmation_service)

def test_write_requires_confirmation(executor):
    result = IntentResult(
        intent=AgentIntent.UPDATE_ORDER_STATUS,
        confidence=1.0,
        entities={"order_id": "OR603", "new_status": "Shipped"}
    )
    with pytest.raises(ConfirmationRequiredError) as exc_info:
        executor.execute(result)
    
    assert "Pending Action" not in str(exc_info.value) # the message is "Confirmation required."
    assert exc_info.value.action_details["target"] == ["OR603"]
    assert exc_info.value.action_details["new_value"] == "Shipped"

def test_confirmation_execution(executor, confirmation_service):
    # Step 1: Request write
    result = IntentResult(
        intent=AgentIntent.UPDATE_COMMITMENT_DATE,
        confidence=1.0,
        entities={"order_id": "OR603", "new_commitment_date": "2026-08-15"}
    )
    try:
        executor.execute(result)
        pytest.fail("Should have raised ConfirmationRequiredError")
    except ConfirmationRequiredError as e:
        conf_id = e.pending_action_id
        
    # Step 2: Confirm
    confirm_result = IntentResult(
        intent=AgentIntent.CONFIRM_ACTION,
        confidence=1.0,
        entities={"confirmation_id": conf_id}
    )
    data = executor.execute(confirm_result)
    assert data.commitment_date == "2026-08-15"

def test_invalid_confirmation_id(executor):
    confirm_result = IntentResult(
        intent=AgentIntent.CONFIRM_ACTION,
        confidence=1.0,
        entities={"confirmation_id": "invalid-id"}
    )
    from app.agent.exceptions import ExecutionError
    with pytest.raises(ExecutionError, match="Confirmation expired or invalid"):
        executor.execute(confirm_result)
