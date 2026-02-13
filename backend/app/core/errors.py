"""
Improved Error Handling Utilities
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error with status code and details"""
    def __init__(self, status_code: int, detail: str, error_code: Optional[str] = None):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(self.detail)


class ValidationError(APIError):
    """Validation error (400)"""
    def __init__(self, detail: str):
        super().__init__(400, detail, "VALIDATION_ERROR")


class NotFoundError(APIError):
    """Resource not found (404)"""
    def __init__(self, resource: str, identifier: str):
        super().__init__(404, f"{resource} not found: {identifier}", "NOT_FOUND")


class ConflictError(APIError):
    """Resource conflict (409)"""
    def __init__(self, detail: str):
        super().__init__(409, detail, "CONFLICT")


class ServiceError(APIError):
    """External service error (503)"""
    def __init__(self, service: str, detail: str):
        super().__init__(503, f"{service} service error: {detail}", "SERVICE_ERROR")


async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors"""
    logger.error(f"API Error: {exc.error_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    error_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    logger.error(
        f"Unhandled exception [{error_id}]: {str(exc)}\n"
        f"Path: {request.url.path}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "error_id": error_id,
            "timestamp": datetime.now().isoformat()
        }
    )


def setup_error_handlers(app):
    """Register error handlers with FastAPI app"""
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers registered")
