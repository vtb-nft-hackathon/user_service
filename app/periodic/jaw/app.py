import logging

from app.periodic.cron import CronApplication
from app.periodic.jaw.di import build_container
from app.periodic.jaw.service import JawService

logger = logging.getLogger(__name__)


def create_app() -> CronApplication:
    container = build_container()
    app = CronApplication(JawService, container)

    @app.on_start
    async def start_metrics_server(cron: CronApplication) -> None:
        pass

    return app
