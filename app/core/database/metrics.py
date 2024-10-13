from contextlib import nullcontext
from time import monotonic
from types import TracebackType
from typing import Any

from prometheus_client import Gauge, Histogram

PROMETHEUS_BUCKETS = (0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1, 2, 3, 5, 10, 30, 60)


class DatabaseMetrics:
    connection_acquire_time = Histogram(
        "connection_acquire_time",
        "Connection acquire time",
        buckets=PROMETHEUS_BUCKETS,
        labelnames=["pool_name"],
    )
    connection_acquired_count = Gauge(
        "connection_acquired_count",
        "Connection acquire count",
        labelnames=["pool_name"],
    )
    connection_released_count = Gauge(
        "connection_released_count",
        "Connection release count",
        labelnames=["pool_name"],
    )
    connection_acquire_error_count = Gauge(
        "connection_acquire_error_count",
        "Connection acquire error count",
        labelnames=["pool_name", "error"],
    )
    database_request_time = Histogram(
        "database_request_time",
        "Database request time",
        buckets=PROMETHEUS_BUCKETS,
        labelnames=["pool_name", "query_tag"],
    )
    database_request_count = Gauge(
        "database_request_count",
        "Database request count",
        labelnames=["pool_name", "query_tag"],
    )
    database_request_error_count = Gauge(
        "database_request_error_count",
        "Database request error count",
        labelnames=["pool_name", "query_tag", "error"],
    )
    application_pool_size = Gauge(
        "application_pool_size",
        "Application pool size",
        labelnames=["pool_name"],
    )
    application_pool_idle_size = Gauge(
        "application_pool_idle_size",
        "Application pool idle size",
        labelnames=["pool_name"],
    )
    application_pool_max_size = Gauge(
        "application_pool_max_size",
        "Application pool max size",
        labelnames=["pool_name"],
    )
    database_pool_size = Gauge(
        "database_pool_size",
        "Database pool size by user",
        labelnames=["pool_name", "user", "app"],
    )


class DatabaseRequestTimer:
    """
    Таймер для метрик на запросы.

    Пишет метрики:
    - на время выполнения запроса
    - количество успешных запросов
    - количество упавших запросов
    """

    def __init__(self, pool_name: str | None = None, query_tag: str | None = None) -> None:
        self._query_tag = query_tag or "unknown"
        self._pool_name = pool_name or "unknown"

    def __enter__(self) -> "DatabaseRequestTimer":
        self._start = monotonic()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        total = monotonic() - self._start
        DatabaseMetrics.database_request_time.labels(pool_name=self._pool_name, query_tag=self._query_tag).observe(
            total,
        )
        if exc_type is None:
            DatabaseMetrics.database_request_count.labels(pool_name=self._pool_name, query_tag=self._query_tag).inc()
        else:
            DatabaseMetrics.database_request_error_count.labels(
                pool_name=self._pool_name,
                query_tag=self._query_tag,
                error=exc_type.__name__,
            ).inc()


# Разрешаем args, kwargs, чтобы иметь возможность подменить реальный контекст-менеджер, таймер в данном случае
class NullContext(nullcontext):  # type: ignore[type-arg]
    def __init__(self, enter_result: Any = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(enter_result)


TimerContextType = type[DatabaseRequestTimer] | type[NullContext]
TimerContext = DatabaseRequestTimer | NullContext
