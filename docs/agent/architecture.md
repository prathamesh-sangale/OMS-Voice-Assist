# Agent Architecture (Phase 3.1)

The CEO Executive Agent follows a decoupled pipeline architecture that strictly separates natural language understanding from business capabilities.

## High-Level Pipeline
1. **CommandInput**: User text arrives via `/api/agent/command`.
2. **CommandAnalyzer**: Converts text into an `IntentResult`. In Phase 3.1, this is a deterministic rule-based analyzer.
3. **AgentRouter**: Manages validation and clarity checks. Handles `unsupported` and `needs_clarification` states.
4. **AgentExecutor**: The security boundary. It uses a static capability registry to map the resolved intent to a predefined read-only method on the `OMSService`.
5. **AgentResponse**: A structured response is formatted and returned to the UI.

## Key Design Principles
- **Read-Only**: Write capabilities are strictly unsupported at this level.
- **No Direct Data Access**: The Agent must go through the `OMSService`. It never queries the JSON repository directly.
- **Deterministic First**: By building the pipeline on a deterministic analyzer first, we establish reliable execution boundaries before introducing LLMs.
