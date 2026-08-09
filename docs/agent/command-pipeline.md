# Command Pipeline

The flow of a command from the UI to the database and back is deterministic and strictly governed.

```mermaid
flowchart TD
    UI[VoiceCommandCenter] -->|POST text| API[/api/agent/command]
    API --> Router[AgentRouter]
    Router --> Analyzer[CommandAnalyzer]
    
    Analyzer -->|IntentResult| Validation{Valid?}
    
    Validation -->|UNSUPPORTED| Error[Unsupported Response]
    Validation -->|NEEDS_CLARIFICATION| Clarify[Clarification Prompt]
    Validation -->|VALID| Executor[AgentExecutor]
    
    Executor --> |Capability Registry| OMS[OMSService]
    OMS --> Rep[JSONOMSRepository]
    Rep --> Data[(JSON)]
    
    Data --> Rep
    Rep --> OMS
    OMS --> Executor
    
    Executor --> Formatter[ResponseFormatter]
    Formatter --> Router
    Router --> API
    API --> UI
```
