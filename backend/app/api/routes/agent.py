from fastapi import APIRouter, Depends, Request
from app.core.rate_limit import limiter
from app.api.dependencies import get_oms_service
from app.oms.services.oms_service import OMSService
from app.agent.models.command import CommandInput, AgentResponse
from app.agent.analyzer import HybridAnalyzer
from app.agent.resolution.entity_resolver import EntityResolver
from app.agent.llm.mock_provider import FakeLLMProvider
from app.agent.llm.groq_provider import GroqLLMProvider
from app.agent.execution.executor import AgentExecutor
from app.agent.router import AgentRouter
from app.oms.services.write_service import WriteService
from app.agent.execution.confirmation import ConfirmationService
from app.agent.sessions.repository import SessionRepository
from app.agent.sessions.session_service import SessionService

router = APIRouter(prefix="/api/agent", tags=["Agent"])

_confirmation_service = ConfirmationService()
_session_repo = SessionRepository()
_session_service = SessionService(_session_repo)

# Typically these dependencies would be wired in the DI container
# Doing it inline here for Phase 3.1
def get_agent_router(service: OMSService = Depends(get_oms_service)) -> AgentRouter:
    resolver = EntityResolver(service)
    
    # Try using real LLM, fallback to mock if no key
    import os
    if os.getenv("GROQ_API_KEY"):
        llm_provider = GroqLLMProvider()
    else:
        llm_provider = FakeLLMProvider()
        
    analyzer = HybridAnalyzer(resolver, llm_provider)
    
    write_service = WriteService(service)
    executor = AgentExecutor(service, write_service, _confirmation_service)
    
    from app.agent.resolution.target_resolver import TargetResolverService
    target_resolver = TargetResolverService(resolver)
    
    return AgentRouter(analyzer, executor, _session_service, target_resolver)

@router.get("/sessions")
def list_sessions():
    """List recent agent sessions."""
    sessions = _session_repo.list_sessions(limit=50)
    return {"sessions": [s.model_dump() for s in sessions]}

@router.get("/sessions/{session_id}")
def get_session(session_id: str):
    """Get a specific agent session by ID."""
    session = _session_repo.get_session(session_id)
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found")
    return session.model_dump()

@router.post("/command", response_model=AgentResponse)
@limiter.limit("20/minute")
def execute_command(
    request: Request,
    command: CommandInput,
    agent_router: AgentRouter = Depends(get_agent_router)
):
    """
    Submit a natural language text command to the Executive Agent.
    The agent will resolve the intent and return an execution result against the OMS.
    """
    return agent_router.handle_command(command)
