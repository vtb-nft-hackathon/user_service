from collections.abc import Callable

import pytest

from app.periodic.jaw.service import JawService
from app.periodic.jaw.settings import JawCronSettings


@pytest.fixture(scope="session")
def jaw_service_factory() -> Callable[[], JawService]:
    def factory() -> JawService:
        return JawService(
            settings=JawCronSettings(),
        )

    return factory
