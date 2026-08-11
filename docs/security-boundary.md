# Security Boundary & Write Operations

## Current Phase Structure
The OMS system supports both robust reads and controlled writes via the CEO Agent.
The architecture safely allows the FastAPI layer, and subsequently the CEO Agent, to interact with the OMS Service.
Data mutation is strictly isolated and guarded by a confirmation workflow, preventing the LLM from making unilateral changes.

## Future Architecture (Read vs Write)
The CEO Agent mutates OMS state through a specialized Command Service, heavily guarded by Validation and a Confirmation Loop.

### Read Path
```text
Agent -> OMSService -> JSONOMSRepository (Read Only)
```

### Write Path (Implemented)
```text
CEO Voice
    ↓
Agent Intent Parsing (Rule Engine + LLM fallback)
    ↓
OMS Command Service
    ↓
Validation (Does this mutation break state machine rules?)
    ↓
Explicit Confirmation Request (Agent halts and asks user to confirm via UI)
    ↓
User Submits Confirmation ID (!confirm <id>)
    ↓
OMS Mutation & Audit Logging
```

## Security Controls Implemented (Phase 7)
1. **Private Deployment**: The application operates under a strict private deployment model tailored exclusively for the CEO. 
2. **Confirmation Protection**: Destructive/mutative actions require out-of-band confirmation. The Agent generates a pending action with a UUID, halting until the user explicitly approves it.
3. **Data Integrity & Backups**: The JSONOMSRepository maintains root metadata and automatically creates `.bak` backups before executing atomic writes.
4. **Rate Limiting**: High-cost operations (LLM Routing, STT transcription, TTS generation) are protected by IP-based rate limiting via SlowAPI.
5. **Secure Headers**: Added Content-Security-Policy, HSTS, X-Frame-Options, and robust CORS policies to the FastAPI middleware.
