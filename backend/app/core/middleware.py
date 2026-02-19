"""
API Response Optimization Middleware
Provides gzip compression and performance monitoring
"""
from fastapi import Request, Response
from fastapi.responses import Response as FastAPIResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
import time
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to track API performance metrics"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(duration)
        
        # Log slow requests (> 1 second)
        if duration > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {duration:.2f}s"
            )
        
        # Log all requests with timing
        logger.info(
            f"{request.method} {request.url.path} "
            f"completed in {duration:.3f}s - Status: {response.status_code}"
        )
        
        return response


def setup_middleware(app):
    """Configure all optimization middleware"""
    
    # Add gzip compression (compress responses > 1KB)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add performance monitoring
    app.add_middleware(PerformanceMonitoringMiddleware)
    
    logger.info("Optimization middleware configured: GZip compression, Performance monitoring")
