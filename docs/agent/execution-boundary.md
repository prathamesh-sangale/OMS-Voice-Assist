# Execution Boundary & Capability Registry

The **AgentExecutor** serves as the system's primary security boundary between the Agent's reasoning layer and the OMS business logic.

## The Static Capability Registry

The agent does not use reflection, `getattr`, or arbitrary string execution to invoke OMS methods. Instead, it relies on a hardcoded, static dictionary mapping explicitly permitted intents to known `OMSService` methods.

```python
self._registry = {
    AgentIntent.LIST_ORDERS: self._oms_service.list_orders,
    AgentIntent.GET_ORDER: self._oms_service.retrieve_order_details,
    AgentIntent.LIST_TASKS: self._oms_service.list_tasks,
    AgentIntent.GET_ORDER_TASKS: self._oms_service.get_order_tasks,
    AgentIntent.LIST_CUSTOMERS: self._oms_service.get_customer_summary,
    AgentIntent.GET_OVERVIEW: self._oms_service.get_overview_metrics,
    AgentIntent.GET_ANALYTICS: self._oms_service.get_order_analytics,
}
```

## Security Rules
1. **Unregistered Intents**: If the analyzer returns an intent that is not in the registry, the Executor raises an `UnsupportedIntentError`. Execution is denied.
2. **Write Protection**: Methods like `update_order` or `create_task` are intentionally omitted from this registry, making write operations impossible even if the analyzer maliciously or erroneously resolves an intent to them.
3. **No Hallucinations**: Because the execution is strictly mapped, an LLM (once introduced) cannot invent a method name like `delete_all_orders` and have the system run it.
