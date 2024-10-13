from asyncpg import PostgresError
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException

from app.core.database import Connection

technical_router = APIRouter(
    prefix="/technical",
    include_in_schema=False,
    route_class=DishkaRoute,
)


@technical_router.get("/ping")
async def ping() -> str:
    return "pong"


@technical_router.get("/ready")
async def ready(*, connection: FromDishka[Connection]) -> str:
    try:
        await connection.fetch("SELECT version()", timeout=1, tag="ready_check")
    except PostgresError as e:
        raise HTTPException(status_code=500, detail="Database is not ready.") from e
    return "ready"
