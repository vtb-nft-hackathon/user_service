from dishka.entities.depends_marker import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from starlette import status

from app.api.exceptions import NotFoundError
from app.api.responses import ErrorMessage, ErrorResponse, GeneralResponse, SuccessResponse, ValidationError
from app.common.events import UserRegistration
from app.common.models_temp import User
from app.core.di.types import UserEventsPublisher
from app.repositories import WalletRepository
from app.repositories.user.repository import UserRepository

users_router = APIRouter(
    default_response_class=GeneralResponse,
    prefix="/wallet",
    tags=["bone"],
    route_class=DishkaRoute,
)


@users_router.get(
    path="/{bone_id}",
    summary="Получить кость по ID",
    description="Возвращает информацию о кости по ее ID.",
    responses={
        status.HTTP_200_OK: {"description": "Кость с указанным ID.", "model": SuccessResponse[User]},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Ошибка валидации.",
            "model": ErrorResponse[ValidationError],
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Кость с указанным ID не существует.",
            "model": ErrorResponse[ErrorMessage],
        },
    },
)
async def get_bone(bone_id: int, bone_repository: FromDishka[WalletRepository]) -> User:
    bone = await bone_repository.get_by_id(bone_id)

    if not bone:
        raise NotFoundError

    return bone


@users_router.post(
    path="",
    response_model=User,
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
    payload: User,
    user_repository: FromDishka[UserRepository],
    publisher: FromDishka[UserEventsPublisher],
) -> User:
    user = await user_repository.create_user(payload.name)

    event = UserRegistration(user_id=user.id)
    await publisher.publish(event, routing_key="v1.event.registration")
    return user
