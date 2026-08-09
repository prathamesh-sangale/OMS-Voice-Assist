from fastapi import APIRouter, Depends
from app.api.dependencies import get_oms_service
from app.oms.services.oms_service import OMSService
from app.oms.schemas.api import AnalyticsData

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/orders", response_model=AnalyticsData)
def get_order_analytics(service: OMSService = Depends(get_oms_service)):
    """Retrieve analytical distribution data for orders."""
    return service.get_order_analytics()
