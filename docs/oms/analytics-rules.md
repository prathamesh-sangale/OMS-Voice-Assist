# Analytics Rules

This document governs how the `OMSService` aggregates the raw demo data into business charts without fabricating missing metrics.

## Null / Missing Data Policy
If a field is missing on an order, that order is simply excluded from that specific distribution slice. We do not inject "Unknown", "N/A", or "0" unless that is literally the value in the OMS source.

If a top-level calculation cannot be universally verified across all commercial models in the source (e.g., Total Order Value), it returns `null`.

## Status Aggregations
- **Completed**: Status strings explicitly matching "completed" or "done".
- **Pending**: Status strings containing the word "pending".
- **Needs Revision**: Status strings containing "revision" or "error".
- **Active**: Any status not falling into the above categories.

## Product Distribution
Because the demo JSON data is highly variable, an order might define its products in a flat array (`product_types`), or nested inside an object array (`product_configs`), or both.

**Rule**: 
1. If `product_types` exists and is populated, it is trusted as the primary product list for the order.
2. If `product_types` is empty/null, the system scans `product_configs` and safely extracts the `product` key.
3. It increments the tally for that product.

## Customer Total vs Active Orders
When grouping orders by `client_name` to create a `CustomerView`:
- **Total Orders**: +1 for every order attached to the client name.
- **Active Orders**: +1 only if the order's status is NOT "completed", "done", "cancelled", or "closed".
