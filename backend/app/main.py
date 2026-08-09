from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import orders, tasks, customers, overview, analytics
from app.oms.exceptions import OMSRecordNotFoundError, OMSDataSourceError, OMSDataValidationError

app = FastAPI(
    title="CEO Executive OMS Voice Agent API",
    description="Backend API for the CEO Executive OMS Voice Agent",
    version="1.0.0",
)

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        content={"error": {"code": "DATA_SOURCE_ERROR", "message": "Failed to load data source"}},
    )

@app.exception_handler(OMSDataValidationError)
async def validation_error_exception_handler(request: Request, exc: OMSDataValidationError):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "DATA_VALIDATION_ERROR", "message": "Data source failed schema validation"}},
    )

# Include routers
app.include_router(orders.router)
app.include_router(tasks.router)
app.include_router(customers.router)
app.include_router(overview.router)
app.include_router(analytics.router)

@app.get("/health", tags=["System"])
async def health_check():
    """
    Basic health check endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "API is operational"}
