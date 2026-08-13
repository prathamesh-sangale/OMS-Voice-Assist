from typing import Optional, Dict, Any, List
from datetime import datetime

from .oms_service import OMSService
from .audit import AuditLogger
from ..contracts.commands import UpdateOrderCommand, UpdateOrderStatusCommand, UpdateCommitmentDateCommand, UpdateOrderDestinationCommand, CreateOrderCommand
from ..schemas.oms import OrderSchema
from ..exceptions import OMSRecordNotFoundError

class WriteService:
    """
    Handles business logic and persistence for OMS writes, supporting multi-target operations with partial failures.
    """
    def __init__(self, oms_service: OMSService):
        self._oms = oms_service
        self._audit = AuditLogger()
        self._actor = "CEO"  # Mock authorization

    def update_order_status(self, command: UpdateOrderStatusCommand) -> Dict[str, Any]:
        results = {"success": [], "failed": []}
        
        allowed = ["Pending", "In Progress", "Needs Revision", "Shipped", "Delivered", "Canceled", "Completed", "Active"]
        new_val_formatted = command.new_status.title()

        for oid in command.order_ids:
            try:
                old_order = self._oms.retrieve_order_details(oid)
                old_val = old_order.status
                
                updated_order = self._oms._repository.update_order_status(oid, new_val_formatted)
                
                self._audit.log_event(
                    actor=self._actor,
                    intent="UPDATE_ORDER_STATUS",
                    target=oid,
                    old_value=old_val,
                    new_value=updated_order.status,
                    status="SUCCESS"
                )
                results["success"].append(updated_order)
            except Exception as e:
                self._audit.log_event(
                    actor=self._actor,
                    intent="UPDATE_ORDER_STATUS",
                    target=oid,
                    old_value=None,
                    new_value=command.new_status,
                    status="FAILED",
                    reason=str(e)
                )
                results["failed"].append({"order_id": oid, "reason": str(e)})
                
        return results

    def update_commitment_date(self, command: UpdateCommitmentDateCommand) -> Dict[str, Any]:
        results = {"success": [], "failed": []}
        new_val = command.new_commitment_date.isoformat()

        for oid in command.order_ids:
            try:
                old_order = self._oms.retrieve_order_details(oid)
                old_val = old_order.commitment_date
                
                updated_order = self._oms._repository.update_order_commitment_date(oid, new_val)
                
                self._audit.log_event(
                    actor=self._actor,
                    intent="UPDATE_COMMITMENT_DATE",
                    target=oid,
                    old_value=old_val,
                    new_value=updated_order.commitment_date,
                    status="SUCCESS"
                )
                results["success"].append(updated_order)
            except Exception as e:
                self._audit.log_event(
                    actor=self._actor,
                    intent="UPDATE_COMMITMENT_DATE",
                    target=oid,
                    old_value=None,
                    new_value=new_val,
                    status="FAILED",
                    reason=str(e)
                )
                results["failed"].append({"order_id": oid, "reason": str(e)})
                
        return results

    def update_order_destination(self, command: UpdateOrderDestinationCommand) -> Dict[str, Any]:
        results = {"success": [], "failed": []}
        new_val = command.new_destination

        for oid in command.order_ids:
            try:
                old_order = self._oms.retrieve_order_details(oid)
                old_val = old_order.delivery_city
                
                updated_order = self._oms._repository.update_order_destination(oid, new_val)
                
                self._audit.log_event(
                    actor=self._actor,
                    intent="UPDATE_ORDER_DESTINATION",
                    target=oid,
                    old_value=old_val,
                    new_value=updated_order.delivery_city,
                    status="SUCCESS"
                )
                results["success"].append(updated_order)
            except Exception as e:
                self._audit.log_event(
                    actor=self._actor,
                    intent="UPDATE_ORDER_DESTINATION",
                    target=oid,
                    old_value=None,
                    new_value=new_val,
                    status="FAILED",
                    reason=str(e)
                )
                results["failed"].append({"order_id": oid, "reason": str(e)})
        return results

    def update_order(self, command: UpdateOrderCommand) -> Dict[str, Any]:
        results = {"success": [], "failed": []}
        updates = command.updates

        for oid in command.order_ids:
            try:
                # Assuming old values are tracked for all fields updated, we just say "Multiple Fields" for simplicity
                old_order = self._oms.retrieve_order_details(oid)
                
                updated_order = self._oms._repository.update_order_generic(oid, updates)
                
                self._audit.log_event(
                    actor=self._actor,
                    intent="UPDATE_ORDER",
                    target=oid,
                    old_value="Multiple Fields",
                    new_value=str(updates),
                    status="SUCCESS"
                )
                results["success"].append(updated_order)
            except Exception as e:
                self._audit.log_event(
                    actor=self._actor,
                    intent="UPDATE_ORDER",
                    target=oid,
                    old_value=None,
                    new_value=str(updates),
                    status="FAILED",
                    reason=str(e)
                )
                results["failed"].append({"order_id": oid, "reason": str(e)})
                
        return results

    def create_order(self, command: CreateOrderCommand) -> OrderSchema:
        try:
            created_order = self._oms._repository.create_order(command.model_dump())
            
            self._audit.log_event(
                actor=self._actor,
                intent="CREATE_ORDER",
                target=created_order.id,
                old_value=None,
                new_value="New Order Draft Created",
                status="SUCCESS"
            )
            return created_order
            
        except Exception as e:
            self._audit.log_event(
                actor=self._actor,
                intent="CREATE_ORDER",
                target="NEW",
                old_value=None,
                new_value="Failed Draft",
                status="FAILED",
                reason=str(e)
            )
            raise
