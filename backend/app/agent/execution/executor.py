from typing import Any, Optional
from ...oms.services.oms_service import OMSService
from ...oms.services.write_service import WriteService
from ...oms.contracts.commands import UpdateOrderStatusCommand, UpdateCommitmentDateCommand
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
            
        if result.intent in [AgentIntent.UPDATE_ORDER_STATUS, AgentIntent.UPDATE_COMMITMENT_DATE]:
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
                    raise ExecutionError("Missing required entity: order_id")
                return method(order_id)

            if result.query is not None:
                return method(result.query)
            else:
                from ...oms.contracts.queries import OrderQuery, TaskQuery, CustomerQuery
                if result.intent == AgentIntent.LIST_ORDERS:
                    return method(OrderQuery())
                elif result.intent == AgentIntent.LIST_TASKS:
                    return method(TaskQuery())
                elif result.intent == AgentIntent.LIST_CUSTOMERS:
                    return method(CustomerQuery())
                else:
                    return method()
        except OMSRecordNotFoundError as e:
            raise e
        except Exception as e:
            raise ExecutionError(f"Failed to execute read {result.intent}: {str(e)}")

    def _execute_write(self, result: IntentResult) -> Any:
        order_id = result.entities.get("order_id")
        if not order_id:
            raise ExecutionError("Missing required entity: order_id")

        if not self._auth_service.authorize(result.intent.value, order_id):
            raise AuthorizationError("You do not have permission to execute this operation.")

        try:
            old_order = self._oms_service.retrieve_order_details(order_id)
        except OMSRecordNotFoundError as e:
            raise e

        # If not already confirmed (no confirmation_id in entities), require confirmation
        # Since this is the initial command, it requires confirmation.
        if result.intent == AgentIntent.UPDATE_ORDER_STATUS:
            new_val = result.entities.get("new_status")
            if not new_val:
                raise ExecutionError("Missing required entity: new_status")
                
            action = self._confirmation_service.create_pending_action(
                intent=result.intent.value,
                command_payload={"order_id": order_id, "new_status": new_val},
                description="Update order status",
                target=order_id,
                old_value=old_order.status,
                new_value=new_val
            )
        elif result.intent == AgentIntent.UPDATE_COMMITMENT_DATE:
            new_val = result.entities.get("new_commitment_date_candidate") or result.entities.get("new_commitment_date")
            if not new_val:
                raise ExecutionError("Missing required entity: new_commitment_date")
                
            action = self._confirmation_service.create_pending_action(
                intent=result.intent.value,
                command_payload={"order_id": order_id, "new_commitment_date": new_val},
                description="Update order commitment date",
                target=order_id,
                old_value=old_order.commitment_date,
                new_value=new_val
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
            
        if not self._auth_service.authorize(action.intent, action.target):
            raise AuthorizationError("Not authorized to confirm this action.")
            
        try:
            self._confirmation_service.consume(action_id)
            
            if action.intent == AgentIntent.UPDATE_ORDER_STATUS.value:
                cmd = UpdateOrderStatusCommand(**action.command_payload)
                data = self._write_service.update_order_status(cmd)
            elif action.intent == AgentIntent.UPDATE_COMMITMENT_DATE.value:
                cmd = UpdateCommitmentDateCommand(**action.command_payload)
                data = self._write_service.update_commitment_date(cmd)
            else:
                raise UnsupportedIntentError("Unsupported confirmed action")
                
            return data
        except OMSRecordNotFoundError as e:
            raise e
        except Exception as e:
            raise ExecutionError(f"Failed to execute confirmed action: {e}")

    def _execute_cancel(self, result: IntentResult) -> Any:
        action_id = result.entities.get("confirmation_id")
        if action_id:
            self._confirmation_service.consume(action_id)
        return {"status": "cancelled", "message": "Action cancelled successfully."}
