import logging
from ..oms.services.oms_service import OMSService
from ..oms.exceptions import OMSRecordNotFoundError
from .contracts.agent import CommandAnalyzer
from .models.command import CommandInput, AgentResponse, IntentResult
from .models.intent import AgentIntent
from .execution.executor import AgentExecutor
from .responses.formatter import ResponseFormatter
from .exceptions import UnsupportedIntentError, ExecutionError, ConfirmationRequiredError, AuthorizationError
from .sessions.session_service import SessionService
from .sessions.draft_manager import DraftManager
from .resolution.target_resolver import TargetResolverService

logger = logging.getLogger(__name__)

class AgentRouter:
    """
    Orchestrates the entire agent pipeline:
    CommandInput -> Session -> Analyzer -> TargetResolver -> DraftManager -> Executor -> AgentResponse
    """
    
    def __init__(self, analyzer: CommandAnalyzer, executor: AgentExecutor, session_service: SessionService, target_resolver: TargetResolverService):
        self._analyzer = analyzer
        self._executor = executor
        self._session_service = session_service
        self._target_resolver = target_resolver
        
    def handle_command(self, command: CommandInput) -> AgentResponse:
        # 1. Session Management
        session = self._session_service.get_or_create_session(command.session_id)
        session.add_message(role="user", text=command.text, input_mode=command.source)
        
        # Deterministic Title Generation
        user_messages = [m for m in session.messages if m.role == "user"]
        def format_title_part(t):
            words = [w for w in t.split() if w.lower() not in ('show', 'me', 'the', 'a', 'an', 'only', 'with', 'to', 'go', 'open', 'navigate')]
            return " ".join(words)[:25].title().strip()

        if len(user_messages) == 1 and session.title == "New Conversation":
            session.title = format_title_part(user_messages[0].text)
            if not session.title: session.title = "Command"
        elif len(user_messages) == 2:
            t1 = format_title_part(user_messages[0].text)
            t2 = format_title_part(user_messages[1].text)
            session.title = f"{t1} — {t2}" if t2 else t1
        
        metadata = {
            "execution_type": "read"
        }
        
        # 2. Check for Pending Answer (Bypass Analyzer)
        if self._session_service.process_pending_answer(session, command.text):
            intent_result = IntentResult(
                intent=AgentIntent(session.context.intent),
                confidence=1.0,
                entities=session.context.entities,
                explanation="Resolved from conversation context.",
                metadata={"method": "Conversation Context"}
            )
            intent_result.entities.update(session.context.draft)
            metadata["confidence"] = 1.0
            metadata["explanation"] = intent_result.explanation
        else:
            # Check for verbal confirmation if waiting
            text_lower = command.text.strip().lower()
            import string
            text_clean = text_lower.translate(str.maketrans('', '', string.punctuation))
            if session.context.operation_status == "pending_confirmation":
                if text_clean in ["confirm", "yes", "go ahead", "do it", "approve"]:
                    command.text = f"!confirm {session.context.confirmation_id}"
                elif text_clean in ["cancel", "no", "abort", "stop"]:
                    command.text = f"!cancel {session.context.confirmation_id}"

            # 3. Analyze Command Normally
            intent_result = self._analyzer.analyze(command, session=session)
            metadata["confidence"] = intent_result.confidence
            metadata["explanation"] = intent_result.explanation
            
            session.context.intent = intent_result.intent.value if intent_result.intent else None
            
            # Target Resolution for Write Operations (if not CREATE_ORDER)
            if intent_result.intent in [AgentIntent.UPDATE_ORDER_STATUS, AgentIntent.UPDATE_COMMITMENT_DATE, AgentIntent.UPDATE_ORDER_DESTINATION]:
                # Attempt to resolve target
                resolved_target = self._target_resolver.resolve_target(intent_result, session)
                if resolved_target.is_ambiguous:
                    session.context.operation_status = "collecting"
                    self._session_service.save_session(session)
                    response = AgentResponse(
                        status="needs_clarification",
                        message=resolved_target.clarification_message or "Which order should I update?",
                        intent=intent_result.intent,
                        metadata=metadata,
                        requires_clarification=True,
                        session_id=session.id
                    )
                    session.add_message(role="agent", text=response.message)
                    self._session_service.save_session(session)
                    return response
                else:
                    # Success resolving
                    session.context.target_orders = resolved_target.structured_target
                    intent_result.entities["order_ids"] = resolved_target.order_ids

            if intent_result.intent in [AgentIntent.CREATE_ORDER, AgentIntent.UPDATE_ORDER_STATUS, AgentIntent.UPDATE_COMMITMENT_DATE, AgentIntent.UPDATE_ORDER_DESTINATION]:
                session.context.operation_status = "collecting"
                for k, v in intent_result.entities.items():
                    if k not in ["order_id", "order_ids", "confirmation_id"]: 
                        session.context.draft[k] = v
                if "order_ids" in intent_result.entities:
                    session.context.entities["order_ids"] = intent_result.entities["order_ids"]
                    session.context.draft["order_ids"] = intent_result.entities["order_ids"]
            
            self._session_service.save_session(session)
        
        # 4. Validation & Clarification Check
        if intent_result.intent == AgentIntent.UNSUPPORTED:
            response = AgentResponse(
                status="unsupported",
                message="I can't perform that OMS operation yet.",
                intent=intent_result.intent,
                metadata=metadata,
                session_id=session.id
            )
            session.add_message(role="agent", text=response.message)
            self._session_service.save_session(session)
            return response
            
        if intent_result.intent == AgentIntent.NEEDS_CLARIFICATION:
            response = AgentResponse(
                status="needs_clarification",
                message=intent_result.explanation or "Which order would you like to see?",
                intent=intent_result.intent,
                metadata=metadata,
                requires_clarification=True,
                session_id=session.id
            )
            session.add_message(role="agent", text=response.message)
            self._session_service.save_session(session)
            return response

        # 5. Draft Evaluation (Missing fields check)
        if intent_result.intent in [AgentIntent.CREATE_ORDER, AgentIntent.UPDATE_ORDER_STATUS, AgentIntent.UPDATE_COMMITMENT_DATE, AgentIntent.UPDATE_ORDER_DESTINATION]:
            intent_result.entities.update(session.context.draft)
            if "order_ids" in session.context.entities:
                intent_result.entities["order_ids"] = session.context.entities["order_ids"]
                
            is_complete, missing_field, prompt = DraftManager.evaluate_draft(intent_result.intent.value, session.context.draft)
            
            if not is_complete:
                session.context.pending_field = missing_field
                self._session_service.save_session(session)
                
                response = AgentResponse(
                    status="needs_clarification",
                    message=prompt,
                    intent=intent_result.intent,
                    metadata=metadata,
                    requires_clarification=True,
                    session_id=session.id
                )
                session.add_message(role="agent", text=response.message)
                self._session_service.save_session(session)
                return response
            
        # 6. Execution
        try:
            if intent_result.intent in [
                AgentIntent.NAVIGATE_TO_DASHBOARD, AgentIntent.NAVIGATE_TO_ORDERS, 
                AgentIntent.NAVIGATE_TO_TASKS, AgentIntent.NAVIGATE_TO_ANALYTICS, 
                AgentIntent.NAVIGATE_TO_CUSTOMERS, AgentIntent.NAVIGATE_TO_COMMAND_CENTER
            ]:
                data = {"status": "navigating"}
                message = "Navigating..."
            else:
                data = self._executor.execute(intent_result)
                message = ResponseFormatter.format_success(intent_result.intent, data)
                
                # Check for complete failure during CONFIRM_ACTION
                if intent_result.intent == AgentIntent.CONFIRM_ACTION and isinstance(data, dict):
                    if len(data.get("success", [])) == 0 and len(data.get("failed", [])) > 0:
                        # Override status to error if nothing succeeded
                        return AgentResponse(
                            status="error",
                            message=message,
                            intent=intent_result.intent,
                            metadata=metadata,
                            session_id=session.id
                        )
            
            # Post-execution Context Tracking
            if intent_result.intent in [AgentIntent.CREATE_ORDER, AgentIntent.UPDATE_ORDER_STATUS, AgentIntent.UPDATE_COMMITMENT_DATE, AgentIntent.UPDATE_ORDER_DESTINATION, AgentIntent.CONFIRM_ACTION, AgentIntent.CANCEL_ACTION]:
                session.context.operation_status = "executed"
                session.context.draft = {}
                session.context.pending_field = None
                session.context.target_orders = None
            elif intent_result.intent in [AgentIntent.LIST_ORDERS, AgentIntent.GET_ORDER]:
                # Save read result context for target resolution
                if isinstance(data, list):
                    ids = [o.id for o in data]
                    session.context.last_result_context = {
                        "identifiers": ids,
                        "query_description": "previous query list"
                    }
                elif hasattr(data, "items"):
                    ids = [o.id for o in data.items]
                    session.context.last_result_context = {
                        "identifiers": ids,
                        "query_description": "previous query list"
                    }
                elif hasattr(data, "id"):
                    session.context.last_result_context = {
                        "identifiers": [data.id],
                        "query_description": "previously viewed order"
                    }
                    
            nav_target = None
            response_type = None
            
            if intent_result.intent == AgentIntent.LIST_ORDERS:
                response_type = "order_list"
            elif intent_result.intent == AgentIntent.GET_ORDER:
                response_type = "order_details"
            elif intent_result.intent == AgentIntent.GET_ANALYTICS:
                nav_target = "/analytics"
                response_type = "analytics"
            elif intent_result.intent == AgentIntent.LIST_TASKS:
                nav_target = "/tasks"
                response_type = "task_list"
            elif intent_result.intent == AgentIntent.LIST_CUSTOMERS:
                nav_target = "/customers"
                response_type = "customer_list"
            elif intent_result.intent == AgentIntent.NAVIGATE_TO_DASHBOARD:
                nav_target = "/overview"
                response_type = "navigation"
            elif intent_result.intent == AgentIntent.NAVIGATE_TO_ORDERS:
                nav_target = "/orders"
                response_type = "navigation"
            elif intent_result.intent == AgentIntent.NAVIGATE_TO_TASKS:
                nav_target = "/tasks"
                response_type = "navigation"
            elif intent_result.intent == AgentIntent.NAVIGATE_TO_ANALYTICS:
                nav_target = "/analytics"
                response_type = "navigation"
            elif intent_result.intent == AgentIntent.NAVIGATE_TO_CUSTOMERS:
                nav_target = "/customers"
                response_type = "navigation"
            elif intent_result.intent == AgentIntent.NAVIGATE_TO_COMMAND_CENTER:
                nav_target = "/voice-command"
                response_type = "navigation"
            elif intent_result.intent in [AgentIntent.UPDATE_ORDER_STATUS, AgentIntent.UPDATE_COMMITMENT_DATE, AgentIntent.UPDATE_ORDER_DESTINATION, AgentIntent.CONFIRM_ACTION, AgentIntent.CANCEL_ACTION]:
                response_type = "confirmation"
                
            nav_hint = {"target": nav_target, "reason": response_type} if nav_target else None
                
            response = AgentResponse(
                status="success",
                message=message,
                intent=intent_result.intent,
                data=data,
                metadata=metadata,
                session_id=session.id,
                response_type=response_type,
                navigation=nav_hint
            )
            
            # Save the message with its structured data so it renders correctly on reload
            message_data = None
            if response_type in ["order_list", "order_details"]:
                # Convert Pydantic objects to dicts for JSON serialization in session storage
                if hasattr(data, "model_dump"):
                    message_data = data.model_dump()
                elif hasattr(data, "__dict__"):
                    message_data = vars(data)
                else:
                    message_data = data

            session.add_message(
                role="agent", 
                text=response.message,
                response_type=response_type,
                data=message_data
            )
            self._session_service.save_session(session)
            return response
            
        except OMSRecordNotFoundError:
            missing_id = intent_result.entities.get('order_id', 'Unknown')
            message = ResponseFormatter.format_not_found(missing_id)
            session.add_message(role="agent", text=message)
            self._session_service.save_session(session)
            return AgentResponse(status="error", message=message, intent=intent_result.intent, metadata=metadata, session_id=session.id)
            
        except UnsupportedIntentError as e:
            session.add_message(role="agent", text=str(e))
            self._session_service.save_session(session)
            return AgentResponse(status="unsupported", message=str(e), intent=intent_result.intent, metadata=metadata, session_id=session.id)
            
        except ConfirmationRequiredError as e:
            session.context.operation_status = "pending_confirmation"
            session.context.confirmation_id = e.action_details["id"]
            self._session_service.save_session(session)
            session.add_message(role="agent", text=str(e))
            self._session_service.save_session(session)
            return AgentResponse(
                status="confirmation_required",
                message=str(e),
                intent=intent_result.intent,
                data=e.action_details,
                metadata=metadata,
                requires_clarification=True,
                session_id=session.id
            )
            
        except AuthorizationError as e:
            session.add_message(role="agent", text=str(e))
            self._session_service.save_session(session)
            return AgentResponse(status="error", message=str(e), intent=intent_result.intent, metadata=metadata, session_id=session.id)
            
        except ExecutionError as e:
            logger.error(f"Execution failed: {e}")
            error_msg = str(e)
            message = ResponseFormatter.format_error("Failed to execute command.")
            if "Missing required entity" in error_msg:
                message = f"I understood you want to update the order, but I need more details: {error_msg.split(': ')[-1]} is missing."
                session.add_message(role="agent", text=message)
                self._session_service.save_session(session)
                return AgentResponse(
                    status="needs_clarification",
                    message=message,
                    intent=intent_result.intent,
                    metadata=metadata,
                    requires_clarification=True,
                    session_id=session.id
                )
                
            session.add_message(role="agent", text=message)
            self._session_service.save_session(session)
            return AgentResponse(status="error", message=message, intent=intent_result.intent, metadata=metadata, session_id=session.id)
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            message = "An unexpected system error occurred."
            session.add_message(role="agent", text=message)
            self._session_service.save_session(session)
            return AgentResponse(status="error", message=message, intent=intent_result.intent, metadata=metadata, session_id=session.id)
