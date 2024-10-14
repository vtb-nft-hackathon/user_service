from collections.abc import AsyncIterator
from typing import cast

from dishka import provide, Provider, Scope
from faststream.rabbit import RabbitBroker, RabbitExchange
from web3 import AsyncWeb3, AsyncHTTPProvider

from app.core.database import Connection, create_pool, Pool
from app.core.di.types import UserEventsPublisher, UserEventsExchange, UserServiceBroker
from app.core.settings import Config
from app.repositories import WalletRepository
from app.repositories.user.repository import UserRepository


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
    async def get_users_broker(self, config: Config) -> AsyncIterator[UserServiceBroker]:
        # Per VHost broker
        broker = RabbitBroker(url=config.brokers.users.url)
        await broker.start()

        yield UserServiceBroker(broker)

        await broker.close()

    @provide(scope=Scope.APP)
    async def get_user_events_exchange(self, broker: UserServiceBroker, config: Config) -> UserEventsExchange:
        exchange = RabbitExchange(**config.brokers.users.publishers.users.model_dump())
        await broker.declare_exchange(exchange)
        return UserEventsExchange(exchange)

    @provide(scope=Scope.APP)
    async def get_user_publisher(self, broker: UserServiceBroker, exchange: UserEventsExchange) -> UserEventsPublisher:
        publisher = broker.publisher(exchange=exchange)
        return UserEventsPublisher(publisher)


class RepositoryProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_async_web3(self, config: Config) -> AsyncWeb3:
        return AsyncWeb3(AsyncHTTPProvider(config.web3.rpc_url))

    wallet_repository = provide(WalletRepository, scope=Scope.REQUEST)
    user_repository = provide(UserRepository, scope=Scope.REQUEST)
