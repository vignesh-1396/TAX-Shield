from fastapi import APIRouter
from app.api.v1.endpoints import auth, check, batch, tally

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(check.router, prefix="/compliance", tags=["Compliance"])
api_router.include_router(batch.router, prefix="/batch", tags=["Batch Processing"])
api_router.include_router(tally.router, prefix="/tally", tags=["Tally Integration"])
