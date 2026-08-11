from typing import Optional
from pydantic import BaseModel, Field

class PaginationQuery(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

class OrderQuery(PaginationQuery):
    """Business contract for querying OMS Orders."""
    search: Optional[str] = Field(default=None, description="Search term for order number or client name")
    status: Optional[str] = Field(default=None, description="Exact match on order status")
    business_model: Optional[str] = Field(default=None, description="Exact match on business model")
    product: Optional[str] = Field(default=None, description="Search term for product type or configuration")
    sales_exec: Optional[str] = Field(default=None, description="Exact match on sales executive name")
    quantity: Optional[int] = Field(default=None, description="Exact match on quantity")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by (e.g. commitment_date, quantity, client_name)")
    sort_order: Optional[str] = Field(default="desc", description="Sort order: asc or desc")

class TaskQuery(PaginationQuery):
    """Business contract for querying OMS Tasks."""
    search: Optional[str] = Field(default=None, description="Search term for task notes, stage label, or assigned user")
    status: Optional[str] = Field(default=None, description="Exact match on task status (e.g. done, pending, in_progress)")
    department: Optional[str] = Field(default=None, description="Exact match on department")
    stage: Optional[str] = Field(default=None, description="Exact match on stage key or label")
    order_id: Optional[str] = Field(default=None, description="Exact match on associated order ID")

class CustomerQuery(PaginationQuery):
    """Business contract for querying the derived Customer Summary."""
    search: Optional[str] = Field(default=None, description="Search term for customer client name")
    customer_type: Optional[str] = Field(default=None, description="Exact match on customer type")
    sales_exec: Optional[str] = Field(default=None, description="Exact match on sales executive name")
