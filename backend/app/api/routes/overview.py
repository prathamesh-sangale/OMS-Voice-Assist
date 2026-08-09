from fastapi import APIRouter, Depends
from app.api.dependencies import get_oms_service
from app.oms.services.oms_service import OMSService
from app.oms.schemas.api import OverviewResponse

router = APIRouter(prefix="/api/overview", tags=["Overview"])

@router.get("", response_model=OverviewResponse)
def get_overview(service: OMSService = Depends(get_oms_service)):
    """Retrieve executive overview metrics and recent activity."""
    return service.get_overview_metrics()
