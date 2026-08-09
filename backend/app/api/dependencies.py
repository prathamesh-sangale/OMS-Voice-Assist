from app.oms.repositories.json_repository import JSONOMSRepository
from app.oms.services.oms_service import OMSService

# Instantiate exactly once as a global application singleton.
# This prevents reloading the JSON on every request.
_json_repository = JSONOMSRepository()
_oms_service = OMSService(repository=_json_repository)

def get_oms_service() -> OMSService:
    """Dependency to inject the shared OMSService into API routes."""
    return _oms_service
