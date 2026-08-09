# Security Boundary & Write Operations

## Current Phase Structure (Read-Only)
At present, the OMS system is entirely read-only.
The architecture safely allows the FastAPI layer, and subsequently the future CEO Agent, to safely pull data from the OMS Service.
Data mutation is strictly prohibited at the interface level, service level, and repository level.

## Future Architecture (Read vs Write)
When write capabilities are eventually needed, they must be fundamentally isolated from the read path.

### Read Path (Current)
```text
Agent -> OMSService -> JSONOMSRepository (Read Only)
```

### Write Path (Future Requirement)
The CEO Agent should only be allowed to mutate OMS state through a specialized Command Service, heavily guarded by Auth/Validation.

```text
CEO Voice
    ↓
Agent Intent Parsing
    ↓
OMS Command Service
    ↓
Authentication & Authorization (Who is speaking? Do they have clearance to bypass standard workflow?)
    ↓
Validation (Does this mutation break state machine rules?)
    ↓
Explicit Confirmation (Agent says: "Are you sure you want to approve this order?")
    ↓
OMS Mutation
```

## Authentication & Authorization
Because this Voice Assistant is designed explicitly for the CEO:
1. **Authentication** will be required to verify the user is actually the CEO.
2. **Authorization** will be required because the CEO operates with omnipotent privileges. A standard user agent might only have access to their own tasks. The CEO agent bypasses departmental silos. 

Do NOT implement fake authentication (like hardcoded tokens). These boundaries will be implemented formally when the system connects to production environments.
