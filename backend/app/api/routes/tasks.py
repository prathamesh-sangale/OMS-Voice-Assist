from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import get_oms_service
from app.oms.services.oms_service import OMSService
from app.oms.schemas.oms import OrderTaskSchema
from app.oms.schemas.api import PaginatedResponse
from app.oms.contracts.queries import TaskQuery

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("", response_model=PaginatedResponse[OrderTaskSchema])
def list_tasks(
    search: Optional[str] = Query(None, description="Search term for tasks"),
    status: Optional[str] = Query(None, description="Exact match on task status"),
    department: Optional[str] = Query(None, description="Exact match on department"),
    stage: Optional[str] = Query(None, description="Exact match on stage"),
    order_id: Optional[str] = Query(None, description="Filter by order ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OMSService = Depends(get_oms_service)
):
    """Retrieve a paginated list of OMS tasks with optional filtering."""
    q = TaskQuery(
        search=search,
        status=status,
        department=department,
        stage=stage,
        order_id=order_id,
        page=page,
        page_size=page_size
    )
    return service.list_tasks(q)
