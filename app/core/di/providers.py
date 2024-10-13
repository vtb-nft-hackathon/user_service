from collections.abc import AsyncIterator
from typing import cast

from dishka import provide, Provider, Scope
from faststream.rabbit import RabbitBroker, RabbitExchange

from app.core.database import Connection, create_pool, Pool
from app.core.di.types import BonesPublisher, SkeletorBonesExchange, SkeletorBroker
from app.core.settings import Config
from app.repositories import BonesRepository


class DefaultProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> Config:
        return Config()

    @provide(scope=Scope.APP)
    async def get_pool(self, config: Config) -> AsyncIterator[Pool]:
        pool = await create_pool(
            dsn=config.db.dsn,
            min_size=config.db.min_size,
            max_size=config.db.max_size,
            max_inactive_connection_lifetime=config.db.max_inactive_connection_lifetime,
            config=config.db,
            tag="master",
            application_name="skeletor",
        )
        yield pool
        await pool.close()

    @provide(scope=Scope.REQUEST)
    async def get_connection(self, pool: Pool) -> AsyncIterator[Connection]:
        acquire_context = pool.acquire()
        yield cast(Connection, await acquire_context.__aenter__())
        await acquire_context.__aexit__()


class RabbitProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_skeletor_broker(self, config: Config) -> AsyncIterator[SkeletorBroker]:
        # Per VHost broker
        broker = RabbitBroker(url=config.brokers.skeletor.url)
        await broker.start()

        yield SkeletorBroker(broker)

        await broker.close()

    @provide(scope=Scope.APP)
    async def get_skeletor_bones_exchange(self, broker: SkeletorBroker, config: Config) -> SkeletorBonesExchange:
        exchange = RabbitExchange(**config.brokers.skeletor.publishers.bones.model_dump())
        await broker.declare_exchange(exchange)
        return SkeletorBonesExchange(exchange)

    @provide(scope=Scope.APP)
    async def get_bones_publisher(self, broker: SkeletorBroker, exchange: SkeletorBonesExchange) -> BonesPublisher:
        publisher = broker.publisher(exchange=exchange)
        return BonesPublisher(publisher)


class RepositoryProvider(Provider):
    @provide(scope=Scope.SESSION)
    async def get_bones_provider(self, pool: Pool) -> BonesRepository:
        return BonesRepository(pool)
