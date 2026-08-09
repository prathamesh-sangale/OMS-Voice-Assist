from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import get_oms_service
from app.oms.services.oms_service import OMSService
from app.oms.schemas.api import PaginatedResponse, CustomerView
from app.oms.contracts.queries import CustomerQuery

router = APIRouter(prefix="/api/customers", tags=["Customers"])

@router.get("", response_model=PaginatedResponse[CustomerView])
def get_customers(
    search: Optional[str] = Query(None, description="Search term for customer name"),
    customer_type: Optional[str] = Query(None, description="Filter by customer type"),
    sales_exec: Optional[str] = Query(None, description="Filter by sales executive"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OMSService = Depends(get_oms_service)
):
    """Retrieve a paginated list of customers aggregated from active orders."""
    q = CustomerQuery(
        search=search,
        customer_type=customer_type,
        sales_exec=sales_exec,
        page=page,
        page_size=page_size
    )
    return service.get_customer_summary(q)
