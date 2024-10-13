from fastapi import APIRouter

from app.api.technical.router import technical_router
from app.api.v1.v1_router import v1_router

# Global router /api
api_router = APIRouter(
    prefix="/api",
)
api_router.include_router(v1_router)

routers = (api_router, technical_router)

__all__ = ["routers"]
