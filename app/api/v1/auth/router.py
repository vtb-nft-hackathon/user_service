from datetime import datetime, timedelta

from dishka.entities.depends_marker import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response
from starlette import status
from jwt import encode, decode

from app.api.responses import ErrorMessage, ErrorResponse, GeneralResponse, SuccessResponse, ValidationError
from app.common.events import UserRegistration
from app.common.models.auth.contracts import AuthRequest
from app.common.models.auth.model import RolesEnum
from app.common.models.user_info.contracts import UserInfoResponseSlim
from app.common.models.user_info.model import UserInfoBase
from app.core.di.types import UserEventsPublisher
from app.repositories.user.repository import UserRepository

auth_router = APIRouter(
    default_response_class=GeneralResponse,
    prefix="/auth",
    tags=["bone"],
    route_class=DishkaRoute,
)


@auth_router.get(
    path="/login",
    summary="User login",
    description="",
    responses={
        status.HTTP_200_OK: {"description": "Кость с указанным ID.", "model": SuccessResponse[bool]},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Ошибка валидации.",
            "model": ErrorResponse[ValidationError],
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "model": ErrorResponse[ErrorMessage],
        },
    },
)
async def login_handler(data: AuthRequest, user_repository: FromDishka[UserRepository], response: Response) -> bool:
    user = await user_repository.auth_user(data.login, data.password)

    if not user:
        return False

    response.set_cookie("Authorization", encode({
        "exp": datetime.now() + timedelta(days=7),
        "user_id": user.id,
        "roles": [RolesEnum.WORKER.value],
    }))
    return True


@auth_router.post(
    path="",
    response_model=UserInfoResponseSlim,
    summary="Создать кость",  # TODO: descriptions swagger
    description="Создает кость указанного типа.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Созданная кость.", "model": SuccessResponse[User]},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Ошибка валидации.",
            "model": ErrorResponse[ValidationError],
        },
    },
)
async def register(
    payload: UserInfoBase,
    user_repository: FromDishka[UserRepository],
    publisher: FromDishka[UserEventsPublisher],
) -> UserInfoBase:
    user = await user_repository.create_user(payload.name)

    event = UserRegistration(user_id=user.id)
    await publisher.publish(event, routing_key="v1.event.registration")
    return user
