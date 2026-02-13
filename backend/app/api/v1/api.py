from fastapi import APIRouter
from app.api.v1.endpoints import auth, check, batch, tally, reports, health, monitoring, api_keys, gstr2b, reconciliation

api_router = APIRouter()

# Health checks (no prefix for standard paths)
api_router.include_router(health.router, tags=["Health"])

# API endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(check.router, prefix="/compliance", tags=["Compliance"])
api_router.include_router(batch.router, prefix="/batch", tags=["Batch Processing"])
api_router.include_router(tally.router, prefix="/tally", tags=["Tally Integration"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["API Keys"])
api_router.include_router(gstr2b.router, prefix="/gst", tags=["GSTR-2B"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

# Monitoring endpoints
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])

# Reconciliation endpoints (GSTR-2B)
api_router.include_router(reconciliation.router, prefix="/reconcile", tags=["Reconciliation"])
