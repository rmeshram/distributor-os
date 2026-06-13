from fastapi import APIRouter
from app.api.v1.whatsapp import router as whatsapp_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.mocks import router as mocks_router
from app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(whatsapp_router)
api_router.include_router(ingestion_router)
api_router.include_router(mocks_router)
api_router.include_router(dashboard_router)
