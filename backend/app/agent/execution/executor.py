from typing import Any
from ...oms.services.oms_service import OMSService
from ...oms.exceptions import OMSRecordNotFoundError
from ..models.intent import AgentIntent
from ..models.command import IntentResult
from ..exceptions import ExecutionError, UnsupportedIntentError

class AgentExecutor:
    """
    Executes a validated IntentResult against the OMSService using a strict capability registry.
    This acts as the primary security boundary.
    """
    
    def __init__(self, oms_service: OMSService):
        self._oms_service = oms_service
        
        # Static Capability Registry
        # This explicitly maps an intent to a known, safe, read-only method on the OMSService.
        self._registry = {
            AgentIntent.LIST_ORDERS: self._oms_service.list_orders,
            AgentIntent.GET_ORDER: self._oms_service.retrieve_order_details,
            AgentIntent.LIST_TASKS: self._oms_service.list_tasks,
            AgentIntent.GET_ORDER_TASKS: self._oms_service.get_order_tasks,
            AgentIntent.LIST_CUSTOMERS: self._oms_service.get_customer_summary,
            AgentIntent.GET_OVERVIEW: self._oms_service.get_overview_metrics,
            AgentIntent.GET_ANALYTICS: self._oms_service.get_order_analytics,
        }

    def execute(self, result: IntentResult) -> Any:
        if result.intent not in self._registry:
            raise UnsupportedIntentError(f"Intent {result.intent} is not registered in the capability registry.")
            
        method = self._registry[result.intent]
        
        try:
            # Simple dispatch logic based on the query structure established in Phase 3.1
            if result.query is not None:
                # Some queries might be strings (order_id), some might be Pydantic models (OrderQuery)
                return method(result.query)
            else:
                return method()
        except OMSRecordNotFoundError as e:
            # We raise this up so the router can catch it and format an appropriate response
            raise e
        except Exception as e:
            raise ExecutionError(f"Failed to execute {result.intent}: {str(e)}")
