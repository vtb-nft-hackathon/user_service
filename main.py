from functools import partial

from granian import Granian
from granian.constants import Interfaces, Loops, ThreadModes
from typer import Typer
from uvloop import run

from app.core.settings import Config

manager = Typer()
config = Config()


@manager.command()
def run_api() -> None:
    from app.api.main import register_app

    Granian(
        target="app.api.main:app",
        address=config.api.address,
        port=config.api.port,
        interface=Interfaces.ASGI,
        loop=Loops.uvloop,
        threading_mode=ThreadModes.runtime,
        log_access=True,
        reload=config.debug,
    ).serve(target_loader=partial(register_app, config=config))


@manager.command()
def run_wallet_registration() -> None:
    """User registration consumer for wallet registration"""
    from app.consumers.wallet_creation import create_subscriber
    from app.consumers.main import start_consumer

    run(start_consumer(create_subscriber, config=config))


@manager.command()
def run_jaw_cron() -> None:
    from app.periodic.jaw import create_app

    app = create_app()
    app.run(config=config)


if __name__ == "__main__":
    manager()
