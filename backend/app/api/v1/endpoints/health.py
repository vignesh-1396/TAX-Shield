"""
Health Check Endpoints for Production Monitoring
Provides liveness, readiness, and metrics endpoints
"""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint
    Returns 200 if service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ITC Shield API"
    }


@router.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness probe - checks if service can handle requests
    Verifies database and cache connectivity
    """
    checks = {
        "database": False,
        "cache": False
    }
    
    # Check database connection
    try:
        from app.db.session import get_connection
        with get_connection() as (conn, cursor):
            cursor.execute("SELECT 1")
            checks["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis cache
    try:
        from app.services.cache import cache
        if cache.enabled and cache.client:
            cache.client.ping()
            checks["cache"] = True
        else:
            checks["cache"] = "disabled"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
    
    # Determine overall status
    is_ready = checks["database"] and (checks["cache"] == True or checks["cache"] == "disabled")
    
    if is_ready:
        return {
            "status": "ready",
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "checks": checks,
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/health/live", tags=["Health"])
async def liveness_check():
    """
    Liveness probe - checks if service is alive
    Simple check that returns 200 if process is running
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }
