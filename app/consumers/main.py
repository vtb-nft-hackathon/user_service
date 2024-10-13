from collections.abc import Callable

from dishka import make_async_container
from dishka.integrations.faststream import setup_dishka
from faststream import FastStream

from app.consumers.types import ConsumerFactoryReturnType
from app.core import logs
from app.core.di.providers import DefaultProvider, RabbitProvider, RepositoryProvider
from app.core.settings import Config


async def start_consumer(
    handler_factory: Callable[[Config], ConsumerFactoryReturnType],
    *,
    config: Config,
) -> None:
    logs.setup_log_parameters(config)

    app_container = make_async_container(DefaultProvider(), RabbitProvider(), RepositoryProvider())
    (
        broker,
        *_,
    ) = handler_factory(config)

    app = FastStream(broker)
    setup_dishka(app_container, app, auto_inject=True)

    await app.run()
