from typing import TypeVar, Generic, List, Optional, Dict, Any
from pydantic import BaseModel
from .oms import OrderSchema

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

class APIError(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    error: APIError

class CustomerView(BaseModel):
    client_name: str
    customer_type: Optional[str] = None
    sales_execs: List[str] = []
    loading_cities: List[str] = []
    delivery_cities: List[str] = []
    active_orders: int = 0
    total_orders: int = 0

class OverviewMetrics(BaseModel):
    active_orders: int
    pending_orders: int
    completed_orders: int
    needs_revision: int
    total_order_value: Optional[float] = None

class OverviewResponse(BaseModel):
    metrics: OverviewMetrics
    recent_orders: List[OrderSchema]
    recent_tasks: List[Any]  # Use Any to avoid circular imports or redefining tasks here, we'll cast later or use OrderTaskSchema directly

class AnalyticsDistribution(BaseModel):
    label: str
    value: int

class AnalyticsData(BaseModel):
    business_model: List[AnalyticsDistribution]
    product: List[AnalyticsDistribution]
    order_status: List[AnalyticsDistribution]
    sales_executive: List[AnalyticsDistribution]
    customer_type: List[AnalyticsDistribution]
