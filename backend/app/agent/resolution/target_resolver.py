from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel
from .entity_resolver import EntityResolver
from ..sessions.models import ConversationSession
from ..models.command import IntentResult
from ..normalization.order_id import normalize_order_id

class ResolvedTarget(BaseModel):
    is_ambiguous: bool = False
    order_ids: List[str] = []
    structured_target: Optional[Dict[str, Any]] = None
    clarification_message: Optional[str] = None

class TargetResolverService:
    def __init__(self, entity_resolver: EntityResolver):
        self._entity_resolver = entity_resolver

    def resolve_target(self, intent_result: IntentResult, session: ConversationSession) -> ResolvedTarget:
        """
        Resolves the target order(s) based on strict priority:
        1. Explicit Order ID
        2. Explicit Client/Entity Match
        3. Pending Operation Target
        4. Current Conversation Entity
        5. Previous Result Context
        """
        
        # 1. Positional reference (e.g. "third one")
        if "position_index" in intent_result.entities:
            idx = intent_result.entities["position_index"]
            if session.context.last_result_context and session.context.last_result_context.get("identifiers"):
                identifiers = session.context.last_result_context["identifiers"]
                if idx == -1:
                    resolved_id = identifiers[-1] if identifiers else None
                elif 0 <= idx < len(identifiers):
                    resolved_id = identifiers[idx]
                else:
                    resolved_id = None
                
                if resolved_id:
                    intent_result.entities["order_id"] = resolved_id
                    return ResolvedTarget(
                        order_ids=[resolved_id],
                        structured_target={
                            "type": "single",
                            "order_ids": [resolved_id],
                            "source": "positional_reference",
                            "query_context": {"index": idx}
                        }
                    )
                else:
                    return ResolvedTarget(
                        is_ambiguous=True,
                        clarification_message=f"I couldn't find an order at that position in the previous list."
                    )
            else:
                return ResolvedTarget(
                    is_ambiguous=True,
                    clarification_message="You referred to a position, but I don't have a recent list of orders."
                )

        # 2. Explicit Order ID in current input
        if "order_id" in intent_result.entities:
            order_id = normalize_order_id(intent_result.entities["order_id"])
            intent_result.entities["order_id"] = order_id  # Update entity for downstream
            return ResolvedTarget(
                order_ids=[order_id],
                structured_target={
                    "type": "single",
                    "order_ids": [order_id],
                    "source": "explicit_order_id",
                    "query_context": {}
                }
            )

        # 2. Explicit Client/Entity Match (e.g., "ABC Industries order")
        # For simplicity, we check if `sales_exec_candidate` or `client_candidate` was extracted by rules/LLM
        # But we would need the LLM to extract "client_candidate".
        client = intent_result.entities.get("client_candidate") or intent_result.entities.get("client_name")
        if client:
            res = self._entity_resolver.resolve_customer(client)
            if res.is_ambiguous:
                return ResolvedTarget(
                    is_ambiguous=True,
                    clarification_message=f"I found multiple orders for {client}. Which one should I update?"
                )
            elif res.resolved_value:
                # We need to find the orders for this client.
                # In a real implementation, we'd query the OMS here to get the actual order IDs.
                # Since EntityResolver only returns the exact client string, we must query OMS.
                orders = self._entity_resolver._oms_service._repository.list_orders(search=res.resolved_value)
                # Strict match on client_name
                matched_orders = [o for o in orders if (o.client_name or "").lower() == res.resolved_value.lower()]
                
                if len(matched_orders) == 1:
                    order_id = matched_orders[0].id
                    return ResolvedTarget(
                        order_ids=[order_id],
                        structured_target={
                            "type": "single",
                            "order_ids": [order_id],
                            "source": "explicit_client_match",
                            "query_context": {"client_name": res.resolved_value}
                        }
                    )
                elif len(matched_orders) > 1:
                    return ResolvedTarget(
                        is_ambiguous=True,
                        clarification_message=f"I found {len(matched_orders)} orders for {res.resolved_value}. Which one should I update?"
                    )
                # If 0, fall through or return error? Fall through.

        # 3. Pending Operation Target
        if session.context.target_orders:
            return ResolvedTarget(
                order_ids=session.context.target_orders["order_ids"],
                structured_target=session.context.target_orders
            )

        # 4. Current Conversation Entity
        if "order_id" in session.context.entities:
            order_id = normalize_order_id(session.context.entities["order_id"])
            session.context.entities["order_id"] = order_id # Update entity for downstream
            return ResolvedTarget(
                order_ids=[order_id],
                structured_target={
                    "type": "single",
                    "order_ids": [order_id],
                    "source": "current_conversation_entity",
                    "query_context": {}
                }
            )
        elif "order_ids" in session.context.entities and session.context.entities["order_ids"]:
            order_id = normalize_order_id(session.context.entities["order_ids"][0])
            return ResolvedTarget(
                order_ids=[order_id],
                structured_target={
                    "type": "single",
                    "order_ids": [order_id],
                    "source": "current_conversation_entity",
                    "query_context": {}
                }
            )

        # 5. Previous Result Context
        if session.context.last_result_context and session.context.last_result_context.get("identifiers"):
            order_ids = session.context.last_result_context["identifiers"]
            query_desc = session.context.last_result_context.get("query_description", "previous query")
            return ResolvedTarget(
                order_ids=order_ids,
                structured_target={
                    "type": "order_set",
                    "order_ids": order_ids,
                    "source": "previous_query",
                    "query_context": {"description": query_desc}
                }
            )

        # Cannot resolve
        return ResolvedTarget(
            is_ambiguous=True,
            clarification_message="Which order should I update?"
        )
