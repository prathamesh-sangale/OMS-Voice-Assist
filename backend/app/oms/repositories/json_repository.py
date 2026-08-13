import json
import os
from typing import List, Optional
from pydantic import ValidationError

from .base import BaseOMSRepository
from ..schemas.oms import OrderSchema, OrderTaskSchema
from ..exceptions import OMSDataSourceError, OMSRecordNotFoundError, OMSDataValidationError

import threading

class JSONOMSRepository(BaseOMSRepository):
    """
    Concrete implementation of the OMS Repository using the local JSON demo file.
    """
    
    def __init__(self, file_path: str = "app/data/crystal-oms-demo.json"):
        self.file_path = file_path
        self._orders: List[OrderSchema] = []
        self._tasks: List[OrderTaskSchema] = []
        self._metadata: dict = {}
        self._lock = threading.RLock()
        self._load_data()
        
    def _load_data(self) -> None:
        if not os.path.exists(self.file_path):
            raise OMSDataSourceError(f"Data source file not found at: {self.file_path}")
            
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                
            # Preserve root-level metadata (exclude standard data arrays)
            self._metadata = {k: v for k, v in raw_data.items() if k not in ["oms_orders", "oms_order_tasks"]}
        except json.JSONDecodeError as e:
            raise OMSDataSourceError(f"Failed to parse JSON file: {str(e)}")
            
        try:
            # Parse orders
            for raw_order in raw_data.get("oms_orders", []):
                self._orders.append(OrderSchema(**raw_order))
                
            # Parse tasks
            for raw_task in raw_data.get("oms_order_tasks", []):
                self._tasks.append(OrderTaskSchema(**raw_task))
                
        except ValidationError as e:
            raise OMSDataValidationError(f"Schema validation failed during data load: {str(e)}")

    def _backup_data(self) -> None:
        """Create a backup of the current JSON file before mutation."""
        import shutil
        if os.path.exists(self.file_path):
            backup_path = self.file_path + ".bak"
            try:
                shutil.copy2(self.file_path, backup_path)
            except Exception as e:
                # Log but do not fail the write if backup fails
                import logging
                logging.getLogger(__name__).warning(f"Failed to create backup: {e}")

    def _save_data(self) -> None:
        """Safely write data back to the JSON file."""
        with self._lock:
            data = {**self._metadata}
            data["oms_orders"] = [order.model_dump(mode="json", exclude_unset=True) for order in self._orders]
            data["oms_order_tasks"] = [task.model_dump(mode="json", exclude_unset=True) for task in self._tasks]
            
            # Write to a temporary file first, then replace for atomic-like behavior
            temp_path = self.file_path + ".tmp"
            try:
                self._backup_data()
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                os.replace(temp_path, self.file_path)
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise OMSDataSourceError(f"Failed to write data safely: {str(e)}")

    def list_orders(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        business_model: Optional[str] = None,
        product: Optional[str] = None,
        sales_exec: Optional[str] = None,
        quantity: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "desc"
    ) -> List[OrderSchema]:
        result = self._orders
        
        if search:
            s = search.lower()
            result = [o for o in result if s in (o.order_number or "").lower() or s in (o.client_name or "").lower()]
            
        if status:
            result = [o for o in result if (o.status or "").lower() == status.lower()]
            
        if business_model:
            result = [o for o in result if (o.business_model or "").lower() == business_model.lower()]
            
        if sales_exec:
            result = [o for o in result if (o.sales_exec or "").lower() == sales_exec.lower()]
            
        if product:
            def matches_product(o: OrderSchema, p: str) -> bool:
                p_lower = p.lower().replace("containers", "container").replace("tanks", "tank")
                def check(val: str) -> bool:
                    v = (val or "").lower()
                    return p_lower in v or v in p_lower
                    
                if check(o.product_type):
                    return True
                if any(check(pt) for pt in (o.product_types or [])):
                    return True
                if any(check(pc.product) for pc in (o.product_configs or [])):
                    return True
                return False
            result = [o for o in result if matches_product(o, product)]

        if quantity is not None:
            result = [o for o in result if (o.quantity == quantity or o.quantity == str(quantity))]

        if sort_by:
            reverse = (sort_order or "desc").lower() == "desc"
            
            def get_sort_key(o: OrderSchema):
                val = getattr(o, sort_by.lower(), None)
                # If sorting by a numeric field that might be string like 'quantity'
                if sort_by.lower() == 'quantity' and val is not None:
                    try:
                        return float(val)
                    except ValueError:
                        pass
                if val is None:
                    # Provide an empty string or 0 depending on expected type to avoid None comparison errors
                    return "" if isinstance(val, str) else (0 if isinstance(val, (int, float)) else "")
                return val

            # Use error handling in sort just in case schema fields differ
            try:
                result.sort(key=get_sort_key, reverse=reverse)
            except TypeError:
                pass # Fallback to unsorted if types can't be cleanly compared

        return result

    def get_order(self, order_id: str) -> Optional[OrderSchema]:
        for order in self._orders:
            if order.id == order_id or order.order_number == order_id:
                return order
        raise OMSRecordNotFoundError(f"Order not found with ID: {order_id}")

    def get_tasks_for_order(self, order_id: str) -> List[OrderTaskSchema]:
        return [task for task in self._tasks if task.order_id == order_id]

    def list_tasks(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        department: Optional[str] = None,
        stage: Optional[str] = None,
        order_id: Optional[str] = None
    ) -> List[OrderTaskSchema]:
        result = self._tasks
        
        if search:
            s = search.lower()
            result = [
                t for t in result 
                if s in (t.stage_label or "").lower() 
                or s in (t.notes or "").lower() 
                or s in (t.assigned_to or "").lower()
                or s in (t.id or "").lower()
                or s in (t.order_id or "").lower()
            ]
            
        if status:
            result = [t for t in result if (t.status or "").lower() == status.lower()]
            
        if department:
            result = [t for t in result if (t.department or "").lower() == department.lower()]
            
        if stage:
            result = [t for t in result if (t.stage_key or "").lower() == stage.lower() or (t.stage_label or "").lower() == stage.lower()]
            
        if order_id:
            result = [t for t in result if t.order_id == order_id]
            
        return result

    def update_order_status(self, order_id: str, new_status: str) -> OrderSchema:
        with self._lock:
            for i, order in enumerate(self._orders):
                if order.id == order_id or order.order_number == order_id:
                    # Create a copy with the updated status
                    updated = order.model_copy(update={"status": new_status})
                    self._orders[i] = updated
                    # Save state outside the iteration but inside the lock
                    self._save_data()
                    return updated
            raise OMSRecordNotFoundError(f"Order not found with ID: {order_id}")

    def update_order_commitment_date(self, order_id: str, new_date: str) -> OrderSchema:
        with self._lock:
            for i, order in enumerate(self._orders):
                if order.id == order_id or order.order_number == order_id:
                    updated = order.model_copy(update={"commitment_date": new_date})
                    self._orders[i] = updated
                    self._save_data()
                    return updated
            raise OMSRecordNotFoundError(f"Order not found with ID: {order_id}")

    def update_order_destination(self, order_id: str, new_destination: str) -> OrderSchema:
        with self._lock:
            for i, order in enumerate(self._orders):
                if order.id == order_id or order.order_number == order_id:
                    updated = order.model_copy(update={"delivery_city": new_destination})
                    self._orders[i] = updated
                    self._save_data()
                    return updated
            raise OMSRecordNotFoundError(f"Order not found with ID: {order_id}")

    def update_order_generic(self, order_id: str, updates: dict) -> OrderSchema:
        with self._lock:
            for i, order in enumerate(self._orders):
                if order.id == order_id or order.order_number == order_id:
                    updated = order.model_copy(update=updates)
                    self._orders[i] = updated
                    self._save_data()
                    return updated
            raise OMSRecordNotFoundError(f"Order not found with ID: {order_id}")

    def create_order(self, payload: dict) -> OrderSchema:
        import uuid
        from datetime import datetime
        with self._lock:
            # Generate a simple ID like OR + length
            new_id = f"OR{800 + len(self._orders)}"
            
            order = OrderSchema(
                id=str(uuid.uuid4()),
                order_number=new_id,
                status="Pending",
                current_stage="Draft",
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
                **payload
            )
            
            self._orders.append(order)
            self._save_data()
            return order
