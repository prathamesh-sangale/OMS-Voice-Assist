# OMS API Interface

While most endpoints are read-only for analytics, specific write operations are exposed for traditional UI workflows. Standard responses and paginations strictly apply.

## Pagination Standard
All collection endpoints return the following standard:
```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 0
}
```

## Error Standard
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}
```

## GET `/api/orders`
**Purpose**: Retrieve OMS orders.
**Filters**:
- `search`: String matching order number or client name.
- `status`: Exact match.
- `business_model`: Exact match.
- `product`: Matches product type string.
- `sales_exec`: Exact match.
- `sort_by`: Field to sort by (e.g., `created_at`, `quantity`). Defaults to `created_at`.
- `sort_order`: Sort direction (`asc` or `desc`). Defaults to `desc`.

## GET `/api/orders/{order_id}`
**Purpose**: Retrieve a single order by ID.
**Errors**: 404 `NOT_FOUND` if order does not exist.

## PATCH `/api/orders/{order_id}`
**Purpose**: Manually update fields on a single order bypassing the Voice Agent execution flow.
**Body**: A partial `Order` JSON object containing only the fields to be updated.
**Returns**: The fully updated `Order` object.

## GET `/api/orders/{order_id}/tasks`
**Purpose**: Retrieve all workflow tasks specifically tied to an order. Returns a flat list, not paginated.

## GET `/api/tasks`
**Purpose**: Retrieve and search workflow tasks across all orders.
**Filters**:
- `search`: String matching notes, stage label, or assigned user.
- `status`: Exact match (e.g. done, pending).
- `department`: Exact match.
- `stage`: Exact match on stage label or key.
- `order_id`: Exact match.

## GET `/api/customers`
**Purpose**: Retrieve the derived customer directory.
**Filters**:
- `search`: Matches client name.
- `customer_type`: Exact match.
- `sales_exec`: Exact match.

## GET `/api/overview`
**Purpose**: Retrieve high-level executive dashboard metrics.
**Returns**: `OverviewResponse` containing `metrics` (Active, Pending, Completed, Needs Revision, Total Value) and lists of `recent_orders` and `recent_tasks`. Total value will be explicitly `null`.

## GET `/api/analytics/orders`
**Purpose**: Retrieve distribution objects useful for charting.
**Returns**: `AnalyticsData` containing lists of `{ label: string, value: number }` for various business dimensions.

# Agent & Voice Interface

## POST `/api/agent/command`
**Purpose**: Submit a natural language command (text) to the OMS Agent.
**Body**:
```json
{
  "text": "Approve order OR601"
}
```
**Returns**: `CommandResponse` indicating success, needs_clarification, or confirmation_required. If confirmation is required, it includes a `data` object with the UUID to confirm.

## POST `/api/voice/transcribe`
**Purpose**: Transcribe an uploaded audio file containing a spoken command.
**Body**: `multipart/form-data` with a `file` field containing the audio (e.g., WebM, WAV, MP3).
**Returns**: A JSON object containing the `transcript` text and inference metadata. Protected by rate limits.

## POST `/api/voice/tts`
**Purpose**: Generate a Text-to-Speech audio blob from text.
**Body**:
```json
{
  "text": "Order OR601 has been approved."
}
```
**Returns**: Audio file stream (e.g., `audio/mpeg` or `audio/mp3`). Protected by rate limits.
