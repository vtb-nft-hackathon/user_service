import logging
from asyncio import AbstractEventLoop
from collections.abc import Awaitable, Callable, Sequence
from time import monotonic
from typing import Any

import asyncpg
from asyncpg.pool import PoolConnectionProxy

from app.core.database.connection import Connection, init_connection
from app.core.database.metrics import DatabaseMetrics, DatabaseRequestTimer, NullContext
from app.core.settings import DatabaseSettings

logger = logging.getLogger(__name__)


class PoolAcquireContext(asyncpg.pool.PoolAcquireContext):
    def __init__(self, pool, timeout: float, metrics_enabled: bool):
        super().__init__(pool, timeout)
        self._metrics_enabled = metrics_enabled

    async def __aenter__(self) -> Connection:
        start = monotonic()
        try:
            connection: Connection = await super().__aenter__()
            if self._metrics_enabled:
                DatabaseMetrics.connection_acquire_time.labels(pool_name=self.pool.tag).observe(monotonic() - start)
                DatabaseMetrics.connection_acquired_count.labels(pool_name=self.pool.tag).inc()
        except Exception as e:
            if self._metrics_enabled:
                # На случай ошибки все равно записать время
                DatabaseMetrics.connection_acquire_time.labels(pool_name=self.pool.tag).observe(monotonic() - start)
                DatabaseMetrics.connection_acquire_error_count.labels(
                    pool_name=self.pool.tag,
                    error=type(e).__name__,
                ).inc()

            raise

        connection.add_parameters(
            pool_name=self.pool.tag,
            default_execute_timeout=self.pool.default_execute_timeout,
            timer_class=self.pool.timer_class,
        )
        return connection

    async def __aexit__(self, *exc):
        await super().__aexit__(*exc)

        if self._metrics_enabled:
            DatabaseMetrics.connection_released_count.labels(pool_name=self.pool.tag).inc()


class Pool(asyncpg.Pool):
    def __init__(self, *args, tag: str = "unknown", config: DatabaseSettings, **kwargs):
        self.tag = tag
        self.default_acquire_timeout = config.query_acquire_timeout
        self.default_execute_timeout = config.query_execute_timeout
        self.metrics_enabled = config.metrics_core_enabled
        self.timer_class = DatabaseRequestTimer if self.metrics_enabled else NullContext
        super().__init__(*args, **kwargs)

    def acquire(
        self,
        *,
        timeout: float | None = None,
    ) -> PoolAcquireContext:
        if timeout is None:
            timeout = self.default_acquire_timeout

        return PoolAcquireContext(self, timeout, self.metrics_enabled)

    async def execute(self, query: str, *args, tag: str = "unknown", **kwargs) -> Any:
        async with self.acquire() as con:
            return await con.execute(query, *args, tag=tag, **kwargs)

    async def executemany(self, command: str, args: Sequence[Any], *, tag: str = "unknown", **kwargs) -> Any:
        async with self.acquire() as con:
            return await con.executemany(command, args, tag=tag, **kwargs)

    async def fetch(self, query, *args, tag: str = "unknown", **kwargs) -> list:
        async with self.acquire() as con:
            return await con.fetch(query, *args, tag=tag, **kwargs)

    async def fetchval(self, query, *args, tag: str = "unknown", **kwargs) -> Any:
        async with self.acquire() as con:
            return await con.fetchval(query, *args, tag=tag, **kwargs)

    async def fetchrow(self, query, *args, tag: str = "unknown", **kwargs) -> Any:
        async with self.acquire() as con:
            return await con.fetchrow(query, *args, tag=tag, **kwargs)

    async def copy_records_to_table(self, table_name: str, *args, tag: str = "unknown", **kwargs) -> Any:
        async with self.acquire() as con:
            return await con.copy_records_to_table(table_name, *args, tag=tag, **kwargs)


def __create_pool(
    dsn: str,
    *args,
    min_size: int = 1,
    max_size: int = 10,
    max_queries: int = 50000,
    max_inactive_connection_lifetime: float = 300.0,
    config: DatabaseSettings,
    setup: Callable[[PoolConnectionProxy], Awaitable[None]] | None = None,
    init: Callable[[Connection], Awaitable[None]] | None = None,
    loop: AbstractEventLoop | None = None,
    connection_class: type[asyncpg.Connection] = asyncpg.Connection,
    record_class: type[asyncpg.Record] = asyncpg.Record,
    tag: str = "master",
    **connect_kwargs,
) -> Pool:
    """Копия asyncpg.create_pool, но возвращает наш объект Pool."""
    return Pool(
        dsn,
        *args,
        connection_class=connection_class,
        record_class=record_class,
        min_size=min_size,
        max_size=max_size,
        max_queries=max_queries,
        loop=loop,
        setup=setup,
        init=init,
        max_inactive_connection_lifetime=max_inactive_connection_lifetime,
        tag=tag,
        config=config,
        **connect_kwargs,
    )


def create_pool(
    dsn: str,
    *args,
    config: DatabaseSettings,
    max_size: int = 10,
    min_size: int = 1,
    loop: AbstractEventLoop | None = None,
    application_name: str = "skeletor-default",
    ssl: bool = False,
    tag: str | None = None,
    **kwargs,
) -> Pool:
    """
    Создание пула подключений к базе.

    Поддерживается корректная обработка jsonb и установка флага application_name.

    .. warning:
       Необходимо использовать эту функцию для работы с БД вместо `asyncpg.create_pool`

    :param dsn: uri подключения к базе данных
    :param config: конфиг базы данных
    :param max_size: максимальный размер пула
    :param min_size: минимальный размер пула
    :param loop: event_loop
    :param application_name: имя приложения для отображения в `pg_stat_activity`
    :param ssl: ssl контекст или False для отключения
    :param tag: Имя пула, передаётся в метрику
    :return: Пул соединений к Postgres
    """
    return __create_pool(
        dsn,
        *args,
        max_size=max_size,
        min_size=min_size,
        init=init_connection,
        server_settings={"application_name": application_name},
        loop=loop,
        connection_class=Connection,
        tag=tag,
        config=config,
        ssl=ssl,
        **kwargs,
    )
