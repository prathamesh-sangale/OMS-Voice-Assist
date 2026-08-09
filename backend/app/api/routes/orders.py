from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.dependencies import get_oms_service
from app.oms.services.oms_service import OMSService
from app.oms.schemas.oms import OrderSchema, OrderTaskSchema
from app.oms.schemas.api import PaginatedResponse
from app.oms.contracts.queries import OrderQuery

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.get("", response_model=PaginatedResponse[OrderSchema])
def list_orders(
    search: Optional[str] = Query(None, description="Search term for orders"),
    status: Optional[str] = Query(None, description="Filter by status"),
    business_model: Optional[str] = Query(None, description="Filter by business model"),
    product: Optional[str] = Query(None, description="Filter by product"),
    sales_exec: Optional[str] = Query(None, description="Filter by sales executive"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OMSService = Depends(get_oms_service)
):
    """Retrieve a paginated list of OMS orders with optional filtering."""
    q = OrderQuery(
        search=search,
        status=status,
        business_model=business_model,
        product=product,
        sales_exec=sales_exec,
        page=page,
        page_size=page_size
    )
    return service.list_orders(q)

@router.get("/{order_id}", response_model=OrderSchema)
def get_order(order_id: str, service: OMSService = Depends(get_oms_service)):
    """Retrieve a specific order by its ID."""
    return service.retrieve_order_details(order_id)

@router.get("/{order_id}/tasks", response_model=list[OrderTaskSchema])
def get_order_tasks(order_id: str, service: OMSService = Depends(get_oms_service)):
    """Retrieve tasks associated with a specific order."""
    return service.get_order_tasks(order_id)
