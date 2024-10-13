from collections.abc import Iterable, Sequence
from typing import Any

import asyncpg

from app.core.database.metrics import TimerContext, TimerContextType

class Connection(asyncpg.Connection[asyncpg.Record]):
    pool_name: str | None
    default_execute_timeout: float | None
    timer_class: TimerContextType

    def add_parameters(
        self,
        pool_name: str,
        default_execute_timeout: float,
        timer_class: TimerContextType,
    ) -> None: ...
    def timer(self, tag: str | None) -> TimerContext: ...
    async def fetch(  # type: ignore[override]
        self,
        query: str,
        *args: Any,
        timeout: float | None = ...,  # noqa: ASYNC109
        tag: str | None = ...,
        **kwargs: Any,
    ) -> list[asyncpg.Record]: ...
    async def fetchval(
        self,
        query: str,
        *args: Any,
        timeout: float | None = ...,  # noqa: ASYNC109
        tag: str | None = ...,
        **kwargs: Any,
    ) -> Any: ...
    async def fetchrow(  # type: ignore[override]
        self,
        query: str,
        *args: Any,
        timeout: float | None = ...,  # noqa: ASYNC109
        tag: str | None = ...,
        **kwargs: Any,
    ) -> asyncpg.Record | None: ...
    async def executemany(
        self,
        command: str,
        args: Iterable[Sequence[object]],
        *,
        timeout: float | None = ...,  # noqa: ASYNC109
        tag: str | None = ...,
        **kwargs: Any,
    ) -> None: ...
    async def execute(
        self,
        query: str,
        *args: Any,
        timeout: float | None = ...,  # noqa: ASYNC109
        tag: str | None = ...,
        **kwargs: Any,
    ) -> str: ...
    async def copy_records_to_table(
        self,
        table_name: str,
        *args: Any,
        timeout: float | None = ...,  # noqa: ASYNC109ЫЫ
        tag: str | None = ...,
        **kwargs: Any,
    ) -> str: ...
    def _check_open(self): ...
    def _drop_local_statement_cache(self): ...
    def _get_reset_query(self): ...

async def init_connection(connection: Connection) -> None: ...
