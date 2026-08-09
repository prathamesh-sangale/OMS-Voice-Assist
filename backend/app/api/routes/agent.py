from fastapi import APIRouter, Depends
from app.api.dependencies import get_oms_service
from app.oms.services.oms_service import OMSService
from app.agent.models.command import CommandInput, AgentResponse
from app.agent.analyzer import RuleEngineAnalyzer
from app.agent.resolution.entity_resolver import EntityResolver
from app.agent.execution.executor import AgentExecutor
from app.agent.router import AgentRouter

router = APIRouter(prefix="/api/agent", tags=["Agent"])

# Typically these dependencies would be wired in the DI container
# Doing it inline here for Phase 3.1
def get_agent_router(service: OMSService = Depends(get_oms_service)) -> AgentRouter:
    resolver = EntityResolver(service)
    analyzer = RuleEngineAnalyzer(resolver)
    executor = AgentExecutor(service)
    return AgentRouter(analyzer, executor)

@router.post("/command", response_model=AgentResponse)
def execute_command(
    command: CommandInput,
    agent_router: AgentRouter = Depends(get_agent_router)
):
    """
    Submit a natural language text command to the Executive Agent.
    The agent will resolve the intent and return an execution result against the OMS.
    """
    return agent_router.handle_command(command)
