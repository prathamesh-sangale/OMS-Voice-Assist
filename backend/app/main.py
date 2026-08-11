import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.routes import orders, tasks, customers, overview, analytics, agent, voice
from app.oms.exceptions import OMSRecordNotFoundError, OMSDataSourceError, OMSDataValidationError
from app.api.middleware import CorrelationIdMiddleware, SecurityHeadersMiddleware
from app.core.rate_limit import limiter

app = FastAPI(
    title="CEO Executive OMS Voice Agent API",
    description="Backend API for the CEO Executive OMS Voice Agent",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS for the frontend
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIdMiddleware)

# Register Global Exception Handlers
@app.exception_handler(OMSRecordNotFoundError)
async def not_found_exception_handler(request: Request, exc: OMSRecordNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "RECORD_NOT_FOUND", "message": str(exc)}},
    )

@app.exception_handler(OMSDataSourceError)
async def source_error_exception_handler(request: Request, exc: OMSDataSourceError):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Failed to load data source"}},
    )

@app.exception_handler(OMSDataValidationError)
async def validation_error_exception_handler(request: Request, exc: OMSDataValidationError):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "VALIDATION_ERROR", "message": "Data source failed schema validation"}},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging
    logging.getLogger(__name__).error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )

# Include routers
app.include_router(orders.router)
app.include_router(tasks.router)
app.include_router(customers.router)
app.include_router(overview.router)
app.include_router(analytics.router)
app.include_router(agent.router)
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])

@app.get("/health", tags=["System"])
async def health_check():
    """
    Basic health check endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "API is operational"}

@app.get("/ready", tags=["System"])
async def ready_check():
    """
    Readiness probe to verify all dependencies are met.
    For this demo, if the app is up, it is ready.
    """
    return {"status": "ready"}
