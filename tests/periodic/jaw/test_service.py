from collections.abc import Callable

from app.periodic.jaw.service import JawService


async def test_service_works(jaw_service_factory: Callable[[], JawService]) -> None:
    service = jaw_service_factory()
    await service.work()

    assert True
