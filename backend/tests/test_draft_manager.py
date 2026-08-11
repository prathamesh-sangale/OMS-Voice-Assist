import pytest
from app.agent.sessions.draft_manager import DraftManager
from app.agent.models.intent import AgentIntent

def test_draft_manager_valid_status():
    draft = {"new_status": "Shipped"}
    is_complete, missing, prompt = DraftManager.evaluate_draft(AgentIntent.UPDATE_ORDER_STATUS.value, draft)
    assert is_complete is True
    assert missing is None

def test_draft_manager_invalid_status():
    draft = {"new_status": "Nothing"}
    is_complete, missing, prompt = DraftManager.evaluate_draft(AgentIntent.UPDATE_ORDER_STATUS.value, draft)
    assert is_complete is False
    assert missing == "new_status"
    assert "valid status" in prompt
    assert draft["new_status"] is None  # Should clear it

def test_draft_manager_valid_destination():
    draft = {"new_destination": "Mumbai"}
    is_complete, missing, prompt = DraftManager.evaluate_draft(AgentIntent.UPDATE_ORDER_DESTINATION.value, draft)
    assert is_complete is True

def test_draft_manager_invalid_destination():
    draft = {"new_destination": "no"}
    is_complete, missing, prompt = DraftManager.evaluate_draft(AgentIntent.UPDATE_ORDER_DESTINATION.value, draft)
    assert is_complete is False
    assert missing == "new_destination"
    assert "valid destination" in prompt

def test_draft_manager_invalid_destination_keyword():
    draft = {"new_destination": "nothing"}
    is_complete, missing, prompt = DraftManager.evaluate_draft(AgentIntent.UPDATE_ORDER_DESTINATION.value, draft)
    assert is_complete is False
    assert missing == "new_destination"
