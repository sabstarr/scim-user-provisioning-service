"""
SCIM 2.0 Endpoints FastAPI Application

This application provides SCIM 2.0 compliant endpoints for user provisioning
with support for multiple realms, secure authentication, and bulk user import capabilities.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn

from .models import create_tables
from .endpoints.scim_endpoints import router as scim_router
from .endpoints.admin_endpoints import router as admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="SCIM 2.0 Endpoints",
    description="SCIM 2.0 compliant endpoints for user provisioning with multi-realm support and bulk CSV import",
    version="1.1.0",  # Updated version for bulk import feature
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scim_router, prefix="", tags=["SCIM"])
app.include_router(admin_router, prefix="", tags=["Admin"])

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with SCIM error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
            "detail": exc.detail,
            "status": str(exc.status_code)
        }
    )

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    logger.info("Starting SCIM 2.0 Endpoints application...")
    create_tables()
    logger.info("Database tables initialized successfully")

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with application information."""
    return {
        "message": "SCIM 2.0 Endpoints API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/admin/health"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Public health check endpoint."""
    return {"status": "healthy", "service": "SCIM 2.0 Endpoints"}

if __name__ == "__main__":
    # For development only - use proper ASGI server in production
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
