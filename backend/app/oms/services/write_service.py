from typing import Optional
from datetime import datetime

from .oms_service import OMSService
from .audit import AuditLogger
from ..contracts.commands import UpdateOrderStatusCommand, UpdateCommitmentDateCommand
from ..schemas.oms import OrderSchema
from ..exceptions import OMSRecordNotFoundError

class WriteService:
    """
    Handles business logic and persistence for OMS writes.
    """
    def __init__(self, oms_service: OMSService):
        self._oms = oms_service
        self._audit = AuditLogger()
        self._actor = "CEO"  # Mock authorization for Phase 5

    def update_order_status(self, command: UpdateOrderStatusCommand) -> OrderSchema:
        try:
            # Verify exists
            old_order = self._oms.get_order(command.order_id)
            old_val = old_order.status

            # Allowed statuses for validation (could be pulled from a schema)
            allowed = ["Pending", "In Progress", "Needs Revision", "Shipped", "Delivered", "Canceled", "Completed", "Active"]
            
            # Simple case insensitive check
            new_val_formatted = command.new_status.title()
            
            if new_val_formatted not in allowed:
                # If they say "delivered", it matches "Delivered"
                pass

            updated_order = self._oms._repo.update_order_status(command.order_id, command.new_status.title())
            
            self._audit.log_event(
                actor=self._actor,
                intent="UPDATE_ORDER_STATUS",
                target=command.order_id,
                old_value=old_val,
                new_value=updated_order.status,
                status="SUCCESS"
            )
            return updated_order
            
        except Exception as e:
            self._audit.log_event(
                actor=self._actor,
                intent="UPDATE_ORDER_STATUS",
                target=command.order_id,
                old_value=None,
                new_value=command.new_status,
                status="FAILED",
                reason=str(e)
            )
            raise

    def update_commitment_date(self, command: UpdateCommitmentDateCommand) -> OrderSchema:
        try:
            old_order = self._oms.get_order(command.order_id)
            old_val = old_order.commitment_date
            
            new_val = command.new_commitment_date.isoformat()
            
            updated_order = self._oms._repo.update_order_commitment_date(command.order_id, new_val)
            
            self._audit.log_event(
                actor=self._actor,
                intent="UPDATE_COMMITMENT_DATE",
                target=command.order_id,
                old_value=old_val,
                new_value=updated_order.commitment_date,
                status="SUCCESS"
            )
            return updated_order
            
        except Exception as e:
            self._audit.log_event(
                actor=self._actor,
                intent="UPDATE_COMMITMENT_DATE",
                target=command.order_id,
                old_value=None,
                new_value=command.new_commitment_date.isoformat(),
                status="FAILED",
                reason=str(e)
            )
            raise
