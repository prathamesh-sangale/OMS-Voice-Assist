from typing import Any, Optional, List
from ...oms.services.oms_service import OMSService
from ...oms.services.write_service import WriteService
from ...oms.contracts.commands import UpdateOrderStatusCommand, UpdateCommitmentDateCommand, UpdateOrderDestinationCommand
from ...oms.exceptions import OMSRecordNotFoundError
from ..models.intent import AgentIntent
from ..models.command import IntentResult
from ..exceptions import ExecutionError, UnsupportedIntentError, ConfirmationRequiredError, AuthorizationError
from .authorization import AuthorizationService
from .confirmation import ConfirmationService

class AgentExecutor:
    """
    Executes a validated IntentResult against the OMSService (Read) and WriteService.
    This acts as the primary security boundary.
    """
    
    def __init__(self, oms_service: OMSService, write_service: WriteService, confirmation_service: ConfirmationService):
        self._oms_service = oms_service
        self._write_service = write_service
        self._confirmation_service = confirmation_service
        self._auth_service = AuthorizationService()
        
        # Static Capability Registry for Reads
        self._read_registry = {
            AgentIntent.LIST_ORDERS: self._oms_service.list_orders,
            AgentIntent.GET_ORDER: self._oms_service.retrieve_order_details,
            AgentIntent.LIST_TASKS: self._oms_service.list_tasks,
            AgentIntent.GET_ORDER_TASKS: self._oms_service.get_order_tasks,
            AgentIntent.LIST_CUSTOMERS: self._oms_service.get_customer_summary,
            AgentIntent.GET_OVERVIEW: self._oms_service.get_overview_metrics,
            AgentIntent.GET_ANALYTICS: self._oms_service.get_order_analytics,
        }

    def execute(self, result: IntentResult) -> Any:
        if result.intent in self._read_registry:
            return self._execute_read(result)
            
        if result.intent in [AgentIntent.CREATE_ORDER, AgentIntent.UPDATE_ORDER]:
            return self._execute_write(result)
            
        if result.intent == AgentIntent.CONFIRM_ACTION:
            return self._execute_confirmation(result)
            
        if result.intent == AgentIntent.CANCEL_ACTION:
            return self._execute_cancel(result)
            
        raise UnsupportedIntentError(f"Intent {result.intent} is not registered in the capability registry.")

    def _execute_read(self, result: IntentResult) -> Any:
        method = self._read_registry[result.intent]
        try:
            if result.intent in [AgentIntent.GET_ORDER, AgentIntent.GET_ORDER_TASKS]:
                order_id = result.entities.get("order_id")
                if not order_id:
                    # In Phase 6, we might have resolved a single order_id into order_ids
                    order_ids = result.entities.get("order_ids")
                    if order_ids and len(order_ids) == 1:
                        order_id = order_ids[0]
                    else:
                        raise ExecutionError("Missing required entity: order_id")
                return method(order_id)

            if result.query is not None:
                return method(result.query)
            else:
                from ...oms.contracts.queries import OrderQuery, TaskQuery, CustomerQuery
                if result.intent == AgentIntent.LIST_ORDERS:
                    valid_keys = OrderQuery.model_fields.keys()
                    kwargs = {k: v for k, v in result.entities.items() if k in valid_keys}
                    return method(OrderQuery(**kwargs))
                elif result.intent == AgentIntent.LIST_TASKS:
                    valid_keys = TaskQuery.model_fields.keys()
                    kwargs = {k: v for k, v in result.entities.items() if k in valid_keys}
                    return method(TaskQuery(**kwargs))
                elif result.intent == AgentIntent.LIST_CUSTOMERS:
                    valid_keys = CustomerQuery.model_fields.keys()
                    kwargs = {k: v for k, v in result.entities.items() if k in valid_keys}
                    return method(CustomerQuery(**kwargs))
                else:
                    return method()
        except OMSRecordNotFoundError as e:
            raise e
        except Exception as e:
            raise ExecutionError(f"Failed to execute read {result.intent}: {str(e)}")

    def _execute_write(self, result: IntentResult) -> Any:
        if result.intent == AgentIntent.CREATE_ORDER:
            if not self._auth_service.authorize(result.intent.value, "NEW"):
                raise AuthorizationError("You do not have permission to execute this operation.")
            
            action = self._confirmation_service.create_pending_action(
                intent=result.intent.value,
                command_payload=result.entities,
                description="Create new order",
                target="NEW",
                old_value=None,
                new_value="New Order Draft"
            )
            raise ConfirmationRequiredError(action.id, action.model_dump())

        # For updates, we need order_ids
        order_ids = result.entities.get("order_ids")
        if not order_ids:
            # Fallback to single order_id
            order_id = result.entities.get("order_id")
            if order_id:
                order_ids = [order_id]
            else:
                raise ExecutionError("Missing required entity: order_ids")

        # Authorize each target
        for oid in order_ids:
            if not self._auth_service.authorize(result.intent.value, oid):
                raise AuthorizationError(f"You do not have permission to execute this operation on {oid}.")

        # For old value tracking in UI, just show a summary if multiple
        old_value = None
        if len(order_ids) == 1:
            try:
                old_order = self._oms_service.retrieve_order_details(order_ids[0])
                if result.intent == AgentIntent.UPDATE_ORDER:
                    old_value = "Multiple Fields"
            except OMSRecordNotFoundError:
                pass
        else:
            old_value = "Multiple Orders"

        # If not already confirmed (no confirmation_id in entities), require confirmation
        if result.intent == AgentIntent.UPDATE_ORDER:
            updates = result.entities.get("updates")
            if not updates or not isinstance(updates, dict):
                raise ExecutionError("Missing required entity: updates")
                
            action = self._confirmation_service.create_pending_action(
                intent=result.intent.value,
                command_payload={"order_ids": order_ids, "updates": updates},
                description=f"Update order fields: {', '.join(updates.keys())}",
                target=order_ids,
                old_value=old_value,
                new_value=str(updates)
            )
        else:
            raise UnsupportedIntentError("Unsupported write operation")
            
        raise ConfirmationRequiredError(
            action.id,
            action.model_dump()
        )

    def _execute_confirmation(self, result: IntentResult) -> Any:
        action_id = result.entities.get("confirmation_id")
        if not action_id:
            raise ExecutionError("Missing confirmation_id")
            
        action = self._confirmation_service.get_and_validate(action_id)
        if not action:
            raise ExecutionError("Confirmation expired or invalid. Please request the change again.")
            
        # Authorize targets
        targets = action.target if isinstance(action.target, list) else [action.target]
        for t in targets:
            if not self._auth_service.authorize(action.intent, t):
                raise AuthorizationError(f"Not authorized to confirm this action on {t}.")
            
        # Re-validate payload to ensure it is still valid
        from ..sessions.draft_manager import DraftManager
        is_complete, missing, _ = DraftManager.evaluate_draft(action.intent, action.command_payload)
        if not is_complete:
            raise ExecutionError(f"Confirmation payload is no longer valid. Missing or invalid field: {missing}")

        try:
            self._confirmation_service.consume(action_id)
            
            if action.intent == AgentIntent.UPDATE_ORDER.value:
                from ...oms.contracts.commands import UpdateOrderCommand
                cmd = UpdateOrderCommand(**action.command_payload)
                data = self._write_service.update_order(cmd)
            elif action.intent == AgentIntent.CREATE_ORDER.value:
                from ...oms.contracts.commands import CreateOrderCommand
                cmd = CreateOrderCommand(**action.command_payload)
                data = self._write_service.create_order(cmd)
            else:
                raise UnsupportedIntentError("Unsupported confirmed action")
                
            return data
        except Exception as e:
            raise ExecutionError(f"Failed to execute confirmed action: {e}")

    def _execute_cancel(self, result: IntentResult) -> Any:
        action_id = result.entities.get("confirmation_id")
        if action_id:
            self._confirmation_service.consume(action_id)
        return {"status": "cancelled", "message": "Action cancelled successfully."}
