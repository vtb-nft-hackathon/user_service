from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import HTTPExceptionHandler

from app.api.exceptions import (
    ApiError,
    handle_404_exception,
    handle_500_exception,
    handle_api_exception,
    handle_validation_exception,
)
from app.core.database import Pool
from app.core.logs import start_async_logging, stop_async_logging
from app.core.settings import Config, Environments


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logging_listener = start_async_logging()
    # Инициализация пула перед стартом приложения.
    await app.state.dishka_container.get(Pool)

    yield

    await app.state.dishka_container.close()
    stop_async_logging(logging_listener)


def create_app(config: Config) -> FastAPI:
    app = FastAPI(
        title="Skeletor",
        description="Скелетор - шаблон для Python-сервисов",
        version=config.version,
        root_path=_construct_root_path(config),
        redoc_url=None,
        lifespan=lifespan,
    )
    _setup_app(app)
    return app


def _setup_app(server: FastAPI) -> None:
    server.add_exception_handler(
        exc_class_or_status_code=ApiError,
        handler=cast(HTTPExceptionHandler, handle_api_exception),
    )
    server.add_exception_handler(
        exc_class_or_status_code=RequestValidationError,
        handler=cast(HTTPExceptionHandler, handle_validation_exception),
    )
    server.add_exception_handler(
        exc_class_or_status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        handler=handle_500_exception,
    )
    server.add_exception_handler(
        exc_class_or_status_code=HTTP_404_NOT_FOUND,
        handler=cast(HTTPExceptionHandler, handle_404_exception),
    )


def _construct_root_path(config: Config) -> str:
    match config.environment:
        case Environments.qa | Environments.prod:
            return "/skeletor"
        case Environments.stage:
            return "/skeletor-stage"
    return ""
