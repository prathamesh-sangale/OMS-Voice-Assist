# OMS Data Model

## Overview
This document outlines the core domain entities derived from the source `crystal-oms-demo.json`. The raw JSON format will be mapped to strict Pydantic schemas within the service layer while maintaining original terminology.

## Entities

### 1. Order (`Order`)
**Purpose**: The central entity representing a commercial transaction.
- **Identifiers**: `id` (UUID), `order_number` (String)
- **Status Fields**: `status`, `current_stage`
- **Core Relationships**:
  - `tasks`: One-to-Many relation with `OrderTask` via `order_id`
  - `product_configs`: One-to-Many relation representing high-level product groupings
  - `containers`: One-to-Many relation representing individual physical assets
- **Important Fields**: `client_name`, `business_model`, `product_type`, `quantity`, `commitment_date`

### 2. Product Configuration (`ProductConfig`)
**Purpose**: Defines the high-level request parameters within an order.
- **Fields**: `product`, `quantity`, `business_model`
- **Relationship**: Embedded inside `Order.product_configs`

### 3. Container (`Container`)
**Purpose**: Represents the physical units associated with an order.
- **Identifiers**: `id` (e.g., `OR601#1`)
- **Important Fields**: `product`, `bm`, `container_no`, `application`
- **Relationship**: Embedded inside `Order.containers`

### 4. Contacts (`Contacts`)
**Purpose**: Groups related contact information found natively on the order.
- **Billing Contact**: Name, Email, Phone, Address
- **Dispatch Contact**: Name, Email, Phone, Address
- **Finance Contact**: Name, Email, Phone

### 5. Order Task (`OrderTask`)
**Purpose**: Represents a workflow stage executed by a department.
- **Identifiers**: `id` (UUID)
- **Relationships**: Links to `Order` via `order_id`
- **Important Fields**: `stage_key`, `department`, `status`, `tat_days`
- **Date Fields**: `planned_date`, `actual_date`, `created_at`, `updated_at`

## Relationships Diagram
```text
Order (oms_orders)
 ├── Customer / Contacts (Embedded)
 ├── Product Configurations (Embedded)
 ├── Containers (Embedded)
 ├── Logistics Details (Embedded)
 └── Workflow Tasks (oms_order_tasks linked via order_id)
```
