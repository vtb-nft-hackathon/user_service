from dishka.entities.depends_marker import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from starlette import status

from app.api.exceptions import NotFoundError
from app.api.responses import ErrorMessage, ErrorResponse, GeneralResponse, SuccessResponse, ValidationError
from app.common.bone import Bone, BoneCreate
from app.common.events import NewBone
from app.core.di.types import BonesPublisher
from app.repositories import BonesRepository

bones_router = APIRouter(
    default_response_class=GeneralResponse,
    prefix="/bones",
    tags=["bone"],
    route_class=DishkaRoute,
)


@bones_router.get(
    path="/{bone_id}",
    summary="Получить кость по ID",
    description="Возвращает информацию о кости по ее ID.",
    responses={
        status.HTTP_200_OK: {"description": "Кость с указанным ID.", "model": SuccessResponse[Bone]},
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
async def get_bone(bone_id: int, bone_repository: FromDishka[BonesRepository]) -> Bone:
    bone = await bone_repository.get_by_id(bone_id)

    if not bone:
        raise NotFoundError

    return bone


@bones_router.post(
    path="",
    response_model=Bone,
    summary="Создать кость",
    description="Создает кость указанного типа.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Созданная кость.", "model": SuccessResponse[Bone]},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Ошибка валидации.",
            "model": ErrorResponse[ValidationError],
        },
    },
)
async def create_bone(
    bone_create: BoneCreate,
    bone_repository: FromDishka[BonesRepository],
    publisher: FromDishka[BonesPublisher],
) -> Bone:
    bone = await bone_repository.add(bone_create)

    event = NewBone(bone_id=bone.id)
    await publisher.publish(event, routing_key="v1.event.created")
    return bone
