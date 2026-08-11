# Agent-OMS Interface Contract

This document outlines the structured capability contract designed specifically for the future CEO Agent.

The Agent should never interact directly with HTTP, JSON keys, file paths, or low-level filters. Instead, the Agent's reasoning layer will instantiate strict Python domain objects (`Queries`) that are passed directly to `OMSService`.

## Agent Query Pattern
```python
# The Agent generates this structured request for reading:
query = OrderQuery(status="pending", product="Dry Container", page=1)

# The Agent executes it via the Service Layer:
response = oms_service.list_orders(query)
```

## Agent Command Pattern (Write Operations)
For mutations, the Agent never writes directly to the database. It generates a structured `Command`:
```python
# The Agent generates an intent to mutate
command = UpdateOrderCommand(order_id="OR123", status="approved")

# The Agent submits the command to the Write Service
# The Write Service halts execution, stores a pending confirmation, and requests user approval.
```

## Available Contracts

### `OrderQuery`
**Purpose**: Ask the system for raw order details.
**Fields**:
- `search`: Optional[str]
- `status`: Optional[str]
- `business_model`: Optional[str]
- `product`: Optional[str]
- `sales_exec`: Optional[str]
- `page`: int
- `page_size`: int

### `TaskQuery`
**Purpose**: Ask the system for workflow and departmental tasks.
**Fields**:
- `search`: Optional[str]
- `status`: Optional[str]
- `department`: Optional[str]
- `stage`: Optional[str]
- `order_id`: Optional[str]
- `page`: int
- `page_size`: int

### `CustomerQuery`
**Purpose**: Ask the system about clients and aggregate history.
**Fields**:
- `search`: Optional[str]
- `customer_type`: Optional[str]
- `sales_exec`: Optional[str]
- `page`: int
- `page_size`: int

### Operations the Agent Can Trigger
The Agent will be given strict tools mapped 1:1 to these `OMSService` methods:
- `oms_service.list_orders(query: OrderQuery)`
- `oms_service.retrieve_order_details(order_id: str)`
- `oms_service.get_order_tasks(order_id: str)`
- `oms_service.list_tasks(query: TaskQuery)`
- `oms_service.get_customer_summary(query: CustomerQuery)`
- `oms_service.get_overview_metrics()`
- `oms_service.get_order_analytics()`

### Write Operations
The Agent may only trigger write operations via strict command objects. Current supported write commands:
- `UpdateOrderCommand(order_id, status)`
- `UpdateCommitmentDateCommand(order_id, date)`

**Strict Boundaries:** The Agent CANNOT write arbitrarily, parse raw files, or execute SQL/pandas functions against the OMS data. All writes must go through the `WriteService` confirmation loop.
