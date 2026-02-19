from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
import logging

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.middleware import setup_middleware
from app.core.security import setup_security_headers
from app.core.errors import setup_error_handlers
from app.api.deps import limiter
from app.db.session import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Setup optimization middleware (gzip, performance monitoring)
setup_middleware(app)

# Setup security headers
setup_security_headers(app)

# Setup error handlers
setup_error_handlers(app)

# Initialize database
@app.on_event("startup")
def startup_db_client():
    logger.info("Starting ITC Shield API...")
    init_database()
    logger.info("Database initialized")
    logger.info(f"API ready at {settings.API_V1_STR}")

@app.on_event("shutdown")
def shutdown():
    logger.info("Shutting down ITC Shield API...")

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
