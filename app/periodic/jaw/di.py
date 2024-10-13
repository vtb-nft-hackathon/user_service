from dishka import AsyncContainer, make_async_container, provide, Provider, Scope

from app.core.di.providers import DefaultProvider
from app.periodic.jaw.service import JawService
from app.periodic.jaw.settings import JawCronSettings


class JawProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> JawCronSettings:
        return JawCronSettings()

    @provide(scope=Scope.APP)
    def service(self, settings: JawCronSettings) -> JawService:
        return JawService(settings)


def build_container() -> AsyncContainer:
    return make_async_container(JawProvider(), DefaultProvider())
