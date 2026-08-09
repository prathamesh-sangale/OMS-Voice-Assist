import json
import os
from typing import List, Optional
from pydantic import ValidationError

from .base import BaseOMSRepository
from ..schemas.oms import OrderSchema, OrderTaskSchema
from ..exceptions import OMSDataSourceError, OMSRecordNotFoundError, OMSDataValidationError

class JSONOMSRepository(BaseOMSRepository):
    """
    Concrete implementation of the OMS Repository using the local JSON demo file.
    """
    
    def __init__(self, file_path: str = "app/data/crystal-oms-demo.json"):
        self.file_path = file_path
        self._orders: List[OrderSchema] = []
        self._tasks: List[OrderTaskSchema] = []
        self._load_data()
        
    def _load_data(self) -> None:
        if not os.path.exists(self.file_path):
            raise OMSDataSourceError(f"Data source file not found at: {self.file_path}")
            
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
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

    def list_orders(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        business_model: Optional[str] = None,
        product: Optional[str] = None,
        sales_exec: Optional[str] = None
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
                p = p.lower()
                if any(p in (pt or "").lower() for pt in (o.product_types or [])):
                    return True
                if any(p in (pc.product or "").lower() for pc in (o.product_configs or [])):
                    return True
                return False
            result = [o for o in result if matches_product(o, product)]

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
            result = [t for t in result if s in (t.stage_label or "").lower() or s in (t.notes or "").lower() or s in (t.assigned_to or "").lower()]
            
        if status:
            result = [t for t in result if (t.status or "").lower() == status.lower()]
            
        if department:
            result = [t for t in result if (t.department or "").lower() == department.lower()]
            
        if stage:
            result = [t for t in result if (t.stage_key or "").lower() == stage.lower() or (t.stage_label or "").lower() == stage.lower()]
            
        if order_id:
            result = [t for t in result if t.order_id == order_id]
            
        return result
