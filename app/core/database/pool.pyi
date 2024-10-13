from asyncio import AbstractEventLoop
from collections.abc import Generator
from typing import Any, Self

import asyncpg

from app.core.database.metrics import TimerContextType
from app.core.settings import DatabaseSettings

class PoolAcquireContext(asyncpg.pool.PoolAcquireContext[asyncpg.Record]):
    pool: Pool

    def __init__(self, pool, timeout: float, metrics_enabled: bool) -> None: ...

class Pool(asyncpg.Pool[asyncpg.Record]):
    tag: str
    default_acquire_timeout: float
    default_execute_timeout: float
    metrics_enabled: bool
    timer_class: TimerContextType

    def __await__(self) -> Generator[Any, None, Self]: ...
    async def _async__init__(self) -> Pool: ...

def create_pool(
    dsn: str,
    *args: Any,
    config: DatabaseSettings,
    max_size: int = 10,
    min_size: int = 1,
    loop: AbstractEventLoop | None = None,
    application_name: str = "skeletor-default",
    ssl: bool = False,
    tag: str | None = None,
    **kwargs: Any,
) -> Pool: ...
