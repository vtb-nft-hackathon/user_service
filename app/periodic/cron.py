import logging
from collections.abc import Awaitable, Callable
from typing import Literal

import aiomisc
from aiomisc import Entrypoint, Service
from aiomisc.service.cron import CronService
from dishka import AsyncContainer

from app.core import logs
from app.core.settings import Config

logger = logging.getLogger(__name__)


Hook = Callable[["CronApplication"], Awaitable[None]]


class CronApplication:
    def __init__(
        self,
        service_type: type[CronService],
        container: AsyncContainer,
        debug: bool = False,
        log_level: Literal["info", "debug"] = "info",
    ):
        self.container = container
        self.service_type = service_type
        self.debug = debug
        self.log_level = log_level
        self._service: CronService | None = None
        self._ready = False
        self._stopped = False
        self._pre_start_hooks: list[Hook] = []
        self._pre_stop_hooks: list[Hook] = []

        @aiomisc.receiver(aiomisc.entrypoint.PRE_START)
        async def run_startup_hooks(entrypoint: Entrypoint, services: tuple[Service, ...]) -> None:
            # Сигнал приходит дважды (баг в aiomisc?), реагируем только на один.
            if self._ready:
                return

            for hook in self._pre_start_hooks:
                await hook(self)

            self._ready = True

        @aiomisc.receiver(aiomisc.entrypoint.PRE_STOP)
        async def run_shutdown_hooks(entrypoint: Entrypoint, services: tuple[Service, ...]) -> None:
            # Сигнал приходит дважды (баг в aiomisc?), реагируем только на один.
            if self._stopped:
                return

            for hook in self._pre_stop_hooks:
                await hook(self)

            # Teardown зависимостей в контейнере.
            await self.container.close()

            self._stopped = True

    @property
    def service(self) -> CronService:
        if self._service is None:
            raise RuntimeError("Service must be initialized first")
        return self._service

    def run(self, *, config: Config) -> None:
        logs.setup_log_parameters(config)

        with aiomisc.entrypoint(debug=self.debug, log_level=self.log_level) as loop:
            loop.create_task(self._bootstrap())
            loop.run_forever()

    def on_start(self, func: Hook) -> Hook:
        self._pre_start_hooks.append(func)
        return func

    def on_stop(self, func: Hook) -> Hook:
        self._pre_stop_hooks.append(func)
        return func

    async def _bootstrap(self) -> None:
        entrypoint = aiomisc.entrypoint.get_current()
        self._service = await self.container.get(self.service_type)
        await entrypoint.start_services(self._service)
