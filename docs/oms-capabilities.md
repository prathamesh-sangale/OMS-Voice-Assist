# OMS Capability Contract

This document outlines what the OMS system currently supports natively based on the demo JSON data.

## Direct OMS Data
Fields derived directly from 1:1 representations in the OMS source.

### Orders
- `id`: The unique system ID (e.g. uuid)
- `order_number`: The readable business number (e.g. OR601)
- `client_name`: Client's legal name
- `status`: The direct status string for the order (e.g., "completed", "pending_approval")
- `business_model`: Sale, Rental, Lease, etc.
- `customer_type`: Enterprise, Mid-Market, etc.
- `sales_exec`: The assigned salesperson
- `loading_city` / `delivery_city`: Core location routing fields.
- `product_types` / `product_configs`: Directly mapped products/configurations linked to the order.
- `quantity`: Kept as raw source string (e.g. "3") on the top level, or integer inside `product_configs`.

### Tasks
- `id`: Task UUID
- `stage_label` / `stage_key`: The identifier for the workflow stage
- `status`: The status string for the task (e.g., "done", "pending", "in_progress")
- `department`: The functional unit responsible
- `created_at` / `updated_at` / `actual_date` / `planned_date`: Workflow temporal markers

## Derived OMS Data
Aggregations safely calculated in real-time by the `OMSService` without fabricating missing structures.

### Customer View
Because there is no "Customer" array in the demo data, `Customers` are uniquely derived by grouping `Orders` via `client_name`.
- `active_orders`: Total orders where `status` is not completed, closed, or cancelled.
- `total_orders`: Total lifetime orders.
- `sales_execs`: A deduplicated list of every sales executive who has handled an order for this client.
- `loading_cities` / `delivery_cities`: Deduplicated lists of cities for this client.

### Overview Metrics
- `active_orders`: Orders not in pending, completed, revision, or error states.
- `pending_orders`: Orders with a status containing "pending".
- `completed_orders`: Orders with "completed" or "done".
- `needs_revision`: Orders with "revision" or "error".
- `total_order_value`: **Currently unsupported (Null)**. A reliable universal calculation rule does not exist across all commercial structures in the demo source.

### Analytics Distributions
Distributions extract counts from all orders, grouping gracefully when data is sparse or missing.
- `Order Status`
- `Business Model`
- `Customer Types`
- `Sales Executives`
- `Products`: Safely groups products by scanning both flat `product_types` arrays and nested `product_configs` arrays.
