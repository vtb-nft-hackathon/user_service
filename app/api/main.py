from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.api import routers
from app.api.application import create_app
from app.core import logs
from app.core.di.providers import DefaultProvider, RabbitProvider, RepositoryProvider
from app.core.settings import Config


def register_app(_: str, *, config: Config) -> FastAPI:
    logs.setup_log_parameters(config=config)
    app = create_app(config)
    for router in routers:
        app.include_router(router)

    container = make_async_container(DefaultProvider(), RabbitProvider(), RepositoryProvider())
    setup_dishka(container, app)
    return app
