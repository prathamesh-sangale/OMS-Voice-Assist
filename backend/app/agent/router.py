import logging
from ..oms.services.oms_service import OMSService
from ..oms.exceptions import OMSRecordNotFoundError
from .contracts.agent import CommandAnalyzer
from .models.command import CommandInput, AgentResponse
from .models.intent import AgentIntent
from .execution.executor import AgentExecutor
from .responses.formatter import ResponseFormatter
from .exceptions import UnsupportedIntentError, ExecutionError, ConfirmationRequiredError, AuthorizationError

logger = logging.getLogger(__name__)

class AgentRouter:
    """
    Orchestrates the entire agent pipeline:
    CommandInput -> Analyzer -> IntentResult -> Validator/Executor -> AgentResponse
    """
    
    def __init__(self, analyzer: CommandAnalyzer, executor: AgentExecutor):
        self._analyzer = analyzer
        self._executor = executor
        
    def handle_command(self, command: CommandInput) -> AgentResponse:
        # 1. Analyze Command
        intent_result = self._analyzer.analyze(command)
        
        metadata = {
            "confidence": intent_result.confidence,
            "explanation": intent_result.explanation,
            "execution_type": "read"
        }
        
        # 2. Validation & Clarification Check
        if intent_result.intent == AgentIntent.UNSUPPORTED:
            return AgentResponse(
                status="unsupported",
                message="I can't perform that OMS operation yet. Write operations are disabled in this phase.",
                intent=intent_result.intent,
                metadata=metadata
            )
            
        if intent_result.intent == AgentIntent.NEEDS_CLARIFICATION:
            return AgentResponse(
                status="needs_clarification",
                message="Which order would you like to see?",
                intent=intent_result.intent,
                metadata=metadata,
                requires_clarification=True
            )
            
        # 3. Execution
        try:
            data = self._executor.execute(intent_result)
            message = ResponseFormatter.format_success(intent_result.intent, data)
            return AgentResponse(
                status="success",
                message=message,
                intent=intent_result.intent,
                data=data,
                metadata=metadata
            )
            
        except OMSRecordNotFoundError:
            # Handle the specific OR999999 case requested
            missing_id = intent_result.entities.get('order_id', 'Unknown')
            return AgentResponse(
                status="error",
                message=ResponseFormatter.format_not_found(missing_id),
                intent=intent_result.intent,
                metadata=metadata
            )
            
        except UnsupportedIntentError as e:
            return AgentResponse(
                status="unsupported",
                message=str(e),
                intent=intent_result.intent,
                metadata=metadata
            )
            
        except ConfirmationRequiredError as e:
            return AgentResponse(
                status="confirmation_required",
                message=str(e),
                intent=intent_result.intent,
                data=e.action_details,
                metadata=metadata,
                requires_clarification=True
            )
            
        except AuthorizationError as e:
            return AgentResponse(
                status="error",
                message=str(e),
                intent=intent_result.intent,
                metadata=metadata
            )
            
        except ExecutionError as e:
            logger.error(f"Execution failed: {e}")
            return AgentResponse(
                status="error",
                message=ResponseFormatter.format_error("Failed to execute command."),
                intent=intent_result.intent,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return AgentResponse(
                status="error",
                message="An unexpected system error occurred.",
                intent=intent_result.intent,
                metadata=metadata
            )
