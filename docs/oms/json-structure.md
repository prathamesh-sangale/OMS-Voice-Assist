# JSON Structure Analysis

The provided `crystal-oms-demo.json` dataset represents a prototype representation of the OMS.

## Top-Level Structure
- `$schema_note`: Schema metadata describing relation between tables.
- `generated_by`: Origin of the file.
- `generated_for`: Timestamp info.
- `warning`: Clarifies this is demo data.
- `counts`: Aggregation statistics (by status, model, product, etc.).
- `oms_orders`: Array of Order entities.
- `oms_order_tasks`: Array of Order Task entities.

## OMS Order (`oms_orders`) Structure
An order contains deeply nested and flat properties representing commercial, logistical, and configuration data.

### Identifiers and Core Data
- `id`: UUID (Primary Key)
- `order_number`: String (e.g., OR601)
- `client_name`: String
- `product_type`, `business_model`, `order_type`, `quantity`, `sales_exec`
- `status`: Lifecycle status (e.g., `pending_approval`, `approved`, `completed`)
- `current_stage`: Workflow stage tracker

### Collections
- `product_types`: Array of strings (e.g., ["Dry Container"])
- `product_configs`: Array of objects detailing requested products, quantity, and business model.
- `containers`: Array of objects detailing individual physical containers (`id`, `product`, `bm`, `application`, etc.)

### Commercial & Logistics Information
- `commitment_date`, `po_received_date`
- `loading_city`, `delivery_city`, `delivery_state`, `transport_mode`
- `transport_in_po`, `transport_remark`

### Contacts
- `billing_name`, `billing_number`, `billing_email`, `billing_address`
- `dispatch_name`, `dispatch_number`, `dispatch_email`, `dispatch_address`
- `finance_name`, `finance_number`, `finance_email`

### Flat Metadata (`meta`)
A highly denormalized dictionary representing granular configurations and commercial pricing dynamically mapped by keys (e.g., `pc_Dry Container_sale_0_price_basic_amount`).

## OMS Order Task (`oms_order_tasks`) Structure
Tasks track the workflow progression of an order through different departments.

- `id`: UUID
- `order_id`: UUID (Foreign Key linking to `oms_orders.id`)
- `stage_key`, `stage_label`: Identifies the task step in the workflow.
- `status`: String (e.g., `done`)
- `department`: String (e.g., `sales`, `logistics`)
- `planned_date`, `actual_date`: Strings (YYYY-MM-DD)
- `tat_days`: Integer
- `assigned_to`, `done_by`, `done_at`: Audit fields
- `notes`: String
