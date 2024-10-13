from fastapi import APIRouter

from app.api.v1.bones.router import bones_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(bones_router)
