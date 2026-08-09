from abc import ABC, abstractmethod
from typing import List, Optional
from ..schemas.oms import OrderSchema, OrderTaskSchema

class BaseOMSRepository(ABC):
    """
    Abstract base class for the OMS Repository.
    Defines the read-only contract for interacting with OMS data.
    """
    
    @abstractmethod
    def list_orders(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        business_model: Optional[str] = None,
        product: Optional[str] = None,
        sales_exec: Optional[str] = None
    ) -> List[OrderSchema]:
        """Returns a list of all orders."""
        pass
        
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[OrderSchema]:
        """Returns a single order by its ID, or raises OMSRecordNotFoundError."""
        pass
        
    @abstractmethod
    def get_tasks_for_order(self, order_id: str) -> List[OrderTaskSchema]:
        """Returns a list of tasks associated with a specific order ID."""
        pass
        
    @abstractmethod
    def list_tasks(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        department: Optional[str] = None,
        stage: Optional[str] = None,
        order_id: Optional[str] = None
    ) -> List[OrderTaskSchema]:
        """Returns a list of all tasks, optionally filtered."""
        pass
