from collections.abc import Awaitable, Callable, Sequence
from typing import Any, TypeVar

import asyncpg
import orjson
from asyncpg.protocol.protocol import BUILTIN_TYPE_NAME_MAP

from app.core.database.metrics import NullContext, TimerContext, TimerContextType

T = TypeVar("T")


def metric_timing(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    async def wrapper(connection: "Connection", *args, tag: str = "unknown", **kwargs: Any) -> Any:
        with connection.timer(tag=tag):
            return await func(connection, *args, **kwargs)

    return wrapper


class Connection(asyncpg.Connection):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.pool_name: str | None = None
        self.default_execute_timeout: float | None = None
        self.timer_class: TimerContextType = NullContext

    def add_parameters(
        self,
        pool_name: str,
        default_execute_timeout: float,
        timer_class: TimerContextType,
    ) -> None:
        self.pool_name = pool_name
        self.default_execute_timeout = default_execute_timeout
        self.timer_class = timer_class

    def timer(self, tag: str) -> TimerContext:
        return self.timer_class(self.pool_name, tag)

    @metric_timing
    async def fetch(
        self,
        query: str,
        *args: Any,
        timeout: float | None = None,  # noqa: ASYNC109
        **kwargs: Any,
    ) -> list[asyncpg.Record]:
        if timeout is None:
            timeout = self.default_execute_timeout

        return await super().fetch(query, *args, timeout=timeout, **kwargs)

    @metric_timing
    async def fetchval(
        self,
        query: str,
        *args: Any,
        timeout: float | None = None,  # noqa: ASYNC109
        **kwargs: Any,
    ) -> Any:
        if timeout is None:
            timeout = self.default_execute_timeout

        return await super().fetchval(query, *args, timeout=timeout, **kwargs)

    @metric_timing
    async def fetchrow(
        self,
        query: str,
        *args: Any,
        timeout: float | None = None,  # noqa: ASYNC109
        **kwargs: Any,
    ) -> asyncpg.Record | None:
        if timeout is None:
            timeout = self.default_execute_timeout

        return await super().fetchrow(query, *args, timeout=timeout, **kwargs)

    @metric_timing
    async def executemany(
        self,
        command: str,
        args: Sequence[Any],
        *,
        timeout: float | None = None,  # noqa: ASYNC109
        **kwargs: Any,
    ) -> None:
        if timeout is None:
            timeout = self.default_execute_timeout

        await super().executemany(command, args, timeout=timeout)

    @metric_timing
    async def execute(
        self,
        query: str,
        *args: Any,
        timeout: float | None = None,  # noqa: ASYNC109
        **kwargs: Any,
    ) -> str:
        if timeout is None:
            timeout = self.default_execute_timeout

        return await super().execute(query, *args, timeout=timeout)

    @metric_timing
    async def copy_records_to_table(
        self,
        table_name: str,
        *args: Any,
        timeout: float | None = None,  # noqa: ASYNC109
        **kwargs: Any,
    ) -> str:
        if timeout is None:
            timeout = self.default_execute_timeout

        return await super().copy_records_to_table(table_name, *args, timeout=timeout, **kwargs)

    async def set_type_codec_fast(
        self,
        typename: str,
        oid: int,
        *,
        schema: str = "public",
        encoder: Callable,
        decoder: Callable,
        format: str = "text",  # noqa: A002
    ) -> None:
        """
        Set an encoder/decoder pair for the specified data type.

        Altered to not use requests to database
        """
        self._check_open()

        self._protocol.get_settings().add_python_codec(oid, typename, schema, [], "scalar", encoder, decoder, format)

        # Statement cache is no longer valid due to codec changes.
        self._drop_local_statement_cache()

    def _get_reset_query(self):
        """Altered to avoid excessive cleanup and additional requests to database."""
        return ""


async def init_connection(connection: Connection) -> None:
    def _encoder(value: str) -> bytes:
        return b"\x01" + orjson.dumps(value)

    def _decoder(value: bytes) -> dict:
        return orjson.loads(value[1:])

    await connection.set_type_codec_fast(
        "jsonb",
        BUILTIN_TYPE_NAME_MAP["jsonb"],
        encoder=_encoder,
        decoder=_decoder,
        schema="pg_catalog",
        format="binary",
    )
