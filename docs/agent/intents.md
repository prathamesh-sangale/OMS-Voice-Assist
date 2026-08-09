# Supported Intents

The following intents represent the current operational capabilities of the Executive Agent.

| Intent | Description | OMS Capability Mapping |
|--------|-------------|------------------------|
| `LIST_ORDERS` | Retrieves paginated orders based on structured filters. | `OMSService.list_orders()` |
| `GET_ORDER` | Fetches details for a specific order by ID or order number. | `OMSService.retrieve_order_details()` |
| `LIST_TASKS` | Retrieves paginated tasks based on structured filters. | `OMSService.list_tasks()` |
| `GET_ORDER_TASKS` | Fetches tasks associated with a specific order. | `OMSService.get_order_tasks()` |
| `LIST_CUSTOMERS` | Aggregates and returns customer profiles from orders. | `OMSService.get_customer_summary()` |
| `GET_OVERVIEW` | Retrieves high-level business metrics and recent activity. | `OMSService.get_overview_metrics()` |
| `GET_ANALYTICS` | Computes aggregation and distribution analytics. | `OMSService.get_order_analytics()` |
| `UNSUPPORTED` | Used when a command (e.g., write/delete) is not allowed. | *None* |
| `NEEDS_CLARIFICATION` | Used when an intent is recognized but lacks mandatory entities. | *None* |

## Supported Rule Patterns
The deterministic rule engine parses natural language variants:

**Orders**
- `show order OR615` -> `GET_ORDER (OR615)`
- `show pending orders` -> `LIST_ORDERS (status=pending)`
- `show completed rental orders for Rohit Menon` -> `LIST_ORDERS (status=completed, business_model=Rental, sales_exec=Rohit Menon)`

**Tasks**
- `show tasks` -> `LIST_TASKS`
- `show pending logistics tasks` -> `LIST_TASKS (status=pending, department=logistics)`
- `show tasks for OR615` -> `GET_ORDER_TASKS (OR615)`

**Customers**
- `show customers` -> `LIST_CUSTOMERS`

**Executive**
- `show overview` -> `GET_OVERVIEW`
- `show analytics` -> `GET_ANALYTICS`
