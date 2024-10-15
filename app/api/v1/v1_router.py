from fastapi import APIRouter

from app.api.v1.auth.router import auth_router
from app.api.v1.user.router import user_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(auth_router)
v1_router.include_router(user_router)
