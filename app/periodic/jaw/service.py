import asyncio
import logging

from aiomisc.service.cron import CronService

from app.periodic.jaw.settings import JawCronSettings

logger = logging.getLogger(__name__)


class JawService(CronService):
    def __init__(
        self,
        settings: JawCronSettings,
    ) -> None:
        super().__init__()
        self.settings = settings

        self.register(self.callback, spec=settings.schedule)

    def __str__(self) -> str:
        return self.__class__.__name__

    async def callback(self) -> None:
        logger.info("Running cron worker.")

        try:
            await self.work()
        except Exception:
            logger.exception("Exception occured during cron worker running.")
        finally:
            logger.info("Cron worker: finish.")

    async def work(self) -> None:
        logger.info("Doing work...")
        await asyncio.sleep(1)
