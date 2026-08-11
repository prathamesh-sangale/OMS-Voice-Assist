import pytest
from unittest.mock import Mock
from app.agent.resolution.target_resolver import TargetResolverService, ResolvedTarget
from app.agent.models.command import IntentResult
from app.agent.models.intent import AgentIntent
from app.agent.sessions.models import ConversationSession, SessionContext

@pytest.fixture
def target_resolver():
    mock_entity_resolver = Mock()
    return TargetResolverService(entity_resolver=mock_entity_resolver)

def test_resolve_positional_reference_valid(target_resolver):
    session = ConversationSession(
        context=SessionContext(
            last_result_context={
                "identifiers": ["OR100", "OR101", "OR102"]
            }
        )
    )
    # the second one
    intent_result = IntentResult(
        intent=AgentIntent.GET_ORDER,
        entities={"position_index": 1},
        confidence=0.9
    )
    
    result = target_resolver.resolve_target(intent_result, session)
    assert result.is_ambiguous is False
    assert result.order_ids == ["OR101"]
    assert intent_result.entities["order_id"] == "OR101"

def test_resolve_positional_reference_out_of_bounds(target_resolver):
    session = ConversationSession(
        context=SessionContext(
            last_result_context={
                "identifiers": ["OR100", "OR101", "OR102"]
            }
        )
    )
    # the fifth one
    intent_result = IntentResult(
        intent=AgentIntent.GET_ORDER,
        entities={"position_index": 4},
        confidence=0.9
    )
    
    result = target_resolver.resolve_target(intent_result, session)
    assert result.is_ambiguous is True
    assert result.order_ids == []
    assert "couldn't find an order at that position" in result.clarification_message

def test_resolve_positional_reference_last(target_resolver):
    session = ConversationSession(
        context=SessionContext(
            last_result_context={
                "identifiers": ["OR100", "OR101", "OR102"]
            }
        )
    )
    # the last one
    intent_result = IntentResult(
        intent=AgentIntent.GET_ORDER,
        entities={"position_index": -1},
        confidence=0.9
    )
    
    result = target_resolver.resolve_target(intent_result, session)
    assert result.is_ambiguous is False
    assert result.order_ids == ["OR102"]

def test_resolve_positional_no_context(target_resolver):
    session = ConversationSession(
        context=SessionContext(
            last_result_context={}
        )
    )
    # the first one
    intent_result = IntentResult(
        intent=AgentIntent.GET_ORDER,
        entities={"position_index": 0},
        confidence=0.9
    )
    
    result = target_resolver.resolve_target(intent_result, session)
    assert result.is_ambiguous is True
    assert "don't have a recent list" in result.clarification_message
