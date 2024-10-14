from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from app.api.responses import GeneralResponse

user_router = APIRouter(
    default_response_class=GeneralResponse,
    prefix="/user",
    tags=["user"],
    route_class=DishkaRoute,
)


@user_router.get(path="/")
async def get_user(user_id: int): ...


@user_router.post(path="/")
async def create_user(user_id: int): ...


@user_router.put(path="/")
async def update_user(user_id: int): ...


@user_router.delete(path="/")
async def delete_user(user_id: int): ...
