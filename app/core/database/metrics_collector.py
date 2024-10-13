import logging
from asyncio import sleep
from enum import Enum

from app.core.database.metrics import DatabaseMetrics
from app.core.database.pool import Pool

logger = logging.getLogger(__name__)


class DatabaseMetricsCollector:
    _get_db_connections = """
        SELECT
            COUNT(1) qty,
            usename,
            application_name
        FROM pg_stat_activity
        GROUP BY usename, application_name;
    """

    def __init__(
        self,
        pools: dict[str, Pool],
        metrics_collect_interval: int,
        collect_pool_metrics: bool,
        collect_database_metrics: bool,
    ) -> None:
        self.pools = pools
        self._with_app = collect_pool_metrics
        self._with_db = collect_database_metrics
        self._metrics_collect_interval = metrics_collect_interval
        self._is_enabled = self._with_db or self._with_app
        self._is_active = False
        self._data: list[tuple[dict[str, str], int]] = []

    @property
    def pool_master(self) -> Pool | None:
        return self.pools.get("master")

    def _write(self) -> None:
        for labels, value in self._data:
            DatabaseMetrics.database_pool_size.labels(**labels).set(value)
        self._data.clear()

    def _collect_app(self, pool_name: str, pool: Pool) -> None:
        """Метрики на уровне приложения."""
        DatabaseMetrics.application_pool_size.labels(pool_name=pool_name).set(pool.get_size())
        DatabaseMetrics.application_pool_idle_size.labels(pool_name=pool_name).set(pool.get_idle_size())
        DatabaseMetrics.application_pool_max_size.labels(pool_name=pool_name).set(pool.get_max_size())

    async def _collect_db(self, pool_name: str, pool: Pool) -> None:
        """Метрики на уровне базы по всем пользователям."""
        res = await pool.fetch(self._get_db_connections)

        for rec in res:
            self._data.append(
                (
                    {
                        "pool_name": pool_name,
                        "user": rec["usename"] or "unknown",
                        "app": rec["application_name"] or "unknown",
                    },
                    rec["qty"],
                ),
            )

    async def _collect(self) -> None:
        for pool_name, pool in self.pools.items():
            if isinstance(pool_name, Enum):
                pool_name = pool_name.value  # в ключах - enum

            # собираем метрику только с мастера, если есть другие пулы, его использующие
            # например, если не задан dsn для read-реплики, то read pool - это ссылка на master pool
            if pool is self.pool_master and pool_name != "master":
                continue

            if self._with_app:
                self._collect_app(pool_name, pool)
            if self._with_db:
                await self._collect_db(pool_name, pool)

    async def run(self) -> None:
        self._is_active = self._is_enabled

        while self._is_active:
            try:
                await sleep(self._metrics_collect_interval)
                await self._collect()
                self._write()
            except Exception:
                logger.exception("%s", self.__class__.__name__)

    async def stop(self) -> None:
        self._is_active = False
