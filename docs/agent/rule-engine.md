# Rule Engine Architecture

The Phase 3.2 Rule Engine replaces simple keyword matching with a scalable, structured rule evaluation pipeline.

## 1. Text Normalization
All incoming text passes through the `TextNormalizer`.
- Converts text to lowercase.
- Strips punctuation (like commas or periods) but preserves IDs (e.g., `OR615`).
- Normalizes multiple spaces.

## 2. Rule Registry & Priority
The `RuleRegistry` manages an explicit list of `CommandRule` implementations.
- **Priority Model**: Rules are evaluated in descending order of priority.
- Example priority:
  - `GetOrderRule` (100) -> Overrides everything if `OR123` is found.
  - `GetOrderTasksRule` (95) -> Overrides generic task list.
  - `ListOrdersFilterRule` (90) -> Overrides generic order list.
  - `ListOrdersGenericRule` (80) -> Catch-all for "show orders".

## 3. Entity Resolution
Rules extract *candidate* entities (e.g., `sales_exec = "Rohit"`).
The `EntityResolver` queries the `OMSService` to resolve candidates against real OMS data.

**Matching Precedence:**
1. Exact match
2. Case-insensitive exact match
3. Fuzzy Candidate Detection (Substring)

**Ambiguity Handling:**
- If a fuzzy match yields multiple candidates (e.g., "Rohit" -> "Rohit Menon", "Rohit Sharma"), the resolver flags the entity as ambiguous.
- The pipeline intercepts this and returns a `NEEDS_CLARIFICATION` state rather than randomly guessing.

## 4. Execution Boundary
The Rule Engine **never** calls a mutating OMS operation and never decides *how* to execute an intent. It only returns an `IntentResult`. The execution remains gated by the `AgentExecutor` Capability Registry.
