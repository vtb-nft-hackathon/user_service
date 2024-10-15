from asyncio import AbstractEventLoop, new_event_loop
from collections.abc import AsyncIterable, AsyncIterator, Iterator
from pathlib import Path

import pytest
import respx
from asyncpg import connect, Connection, Record
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka as setup_fastapi_dishka
from dishka.integrations.faststream import setup_dishka as setup_faststream_dishka
from fastapi import FastAPI
from faststream import FastStream
from httpx import AsyncClient
from respx import MockRouter
from yoyo import get_backend, read_migrations  # type: ignore[import-untyped]

from app.api.application import create_app
from app.consumers.types import ConsumerFactoryReturnType
from app.core.database import Pool
from app.core.di.providers import DefaultProvider, RabbitProvider, RepositoryProvider
from app.core.settings import Config
from app.repositories import WalletRepository


class TestError(Exception):
    pass


@pytest.fixture(scope="session")
def event_loop() -> Iterator[AbstractEventLoop]:
    loop = new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def config() -> Config:
    return Config()


@pytest.fixture(scope="session")
def database_migrations_dir(config: Config) -> Path:
    return Path(__file__).parent.parent / "users-db" / "migrations"


@pytest.fixture(scope="session")
async def db_pool(container: AsyncContainer) -> AsyncIterator[Pool]:
    async with container():
        yield await container.get(Pool)


async def setup_database(conn: "Connection[Record]", database_name: str) -> None:
    await conn.execute(f"CREATE DATABASE {database_name}")


async def teardown_database(conn: "Connection[Record]", database_name: str) -> None:
    await conn.execute(f"DROP DATABASE IF EXISTS {database_name}")


def run_migrations(dsn: str, migrations_path: str) -> None:
    db = get_backend(dsn)

    with db.lock():
        migrations = read_migrations(migrations_path)
        db.apply_migrations(db.to_apply(migrations))


@pytest.fixture(scope="session", autouse=True)
async def _test_database(config: Config, database_migrations_dir: Path) -> AsyncIterator[None]:
    [_, test_db_name] = config.db.dsn.rsplit("/", maxsplit=1)

    # Тестовой БД еще не существует, нужно подключаться к дефолтной.
    default_db_conn = await connect(config.db.dsn, database="postgres")

    await teardown_database(default_db_conn, test_db_name)
    await setup_database(default_db_conn, test_db_name)
    run_migrations(config.db.dsn, str(database_migrations_dir))

    # Теперь можно подключиться к тестовой БД.
    test_db_conn = await connect(config.db.dsn)
    await setup_dirty_tables_tracking(test_db_conn)
    await test_db_conn.close()

    yield

    await teardown_database(default_db_conn, test_db_name)
    await default_db_conn.close()


async def setup_dirty_tables_tracking(conn: "Connection[Record]") -> None:
    """
    Подготавливает инструменты для очистки таблиц после тестирования.

    Во время выполнения теста таблица __dirty_tables отслеживает
    состояние таблиц приложения в столбцах (name, is_dirty).

    При вставке в таблицу триггер mark_dirty вызовет функцию,
    которая поменяет флаг dirty для этой таблицы с FALSE на TRUE.

    По окончанию теста нужно вызвать функцию clean_tables. Она
    очистит все таблицы, которые использовались в тесте.
    """
    create_table_query = """
        CREATE TABLE __dirty_tables (name, is_dirty) AS (
          SELECT relname, FALSE
          FROM pg_class
          WHERE relkind = 'r'
          AND relnamespace = 'public'::regnamespace
        )
    """

    create_mark_dirty_function_query = """
        CREATE FUNCTION mark_dirty()
          RETURNS trigger
          LANGUAGE plpgsql
        AS
        $func$
        BEGIN
          UPDATE __dirty_tables SET is_dirty = TRUE WHERE name = TG_TABLE_NAME;
          RETURN NEW;
        END;
        $func$;
    """

    create_trigger_query = """
        CREATE TRIGGER mark_dirty
        AFTER INSERT ON %s
        EXECUTE FUNCTION mark_dirty();
        """

    create_truncate_function_query = """
        CREATE FUNCTION clean_tables()
          RETURNS void
          LANGUAGE plpgsql
        AS
        $func$
        DECLARE table_name text;
        BEGIN
          FOR table_name in
            SELECT name
            FROM __dirty_tables
            WHERE is_dirty IS TRUE
          LOOP
            EXECUTE format('TRUNCATE TABLE %I RESTART IDENTITY CASCADE', table_name);
          END LOOP;
          UPDATE __dirty_tables SET is_dirty = FALSE;
        END;
        $func$;
    """

    await conn.execute(create_table_query)
    await conn.execute(create_mark_dirty_function_query)
    await conn.execute(create_truncate_function_query)

    for table in await conn.fetch("SELECT name FROM __dirty_tables"):
        await conn.execute(create_trigger_query % table["name"])


@pytest.fixture(autouse=True)
async def _clean_tables(db_pool: Pool) -> AsyncIterable[None]:
    """
    Очищает таблицы, использованные во время выполнения теста.

    Использует функцию БД `clean_tables()`, созданную в `setup_dirty_tables_tracking`.
    """
    yield

    await db_pool.execute("SELECT clean_tables()")


@pytest.fixture(scope="session")
async def container() -> AsyncIterable[AsyncContainer]:
    # Providers can be mocked here by another providers
    container = make_async_container(DefaultProvider(), RabbitProvider(), RepositoryProvider())
    yield container
    await container.close()


@pytest.fixture(scope="session")
def app(config: Config, container: AsyncContainer) -> FastAPI:
    from app.api import routers

    app = create_app(config)

    for router in routers:
        app.include_router(router)

    setup_fastapi_dishka(container, app)
    return app


@pytest.fixture(scope="session")
async def test_client(app: FastAPI) -> AsyncIterable[AsyncClient]:
    # Context manager for startup/shutdown hooks
    async with AsyncClient(app=app, base_url="http://skeletor") as client:
        yield client


@pytest.fixture(scope="session")
async def assign_large_account_consumer(
    config: Config,
    container: AsyncContainer,
) -> ConsumerFactoryReturnType:
    from app.consumers.wallet_creation import create_subscriber

    broker, exchange, queue, handler = create_subscriber(config)
    app = FastStream(broker)
    setup_faststream_dishka(container, app, auto_inject=True)
    return broker, exchange, queue, handler


@pytest.fixture
async def bones_repository(container: AsyncContainer) -> AsyncIterator[WalletRepository]:
    async with container() as request_container:
        yield await request_container.get(WalletRepository)


@pytest.fixture
def offers_api_router(config: Config) -> Iterator[MockRouter]:
    with respx.mock(base_url=config.clients.offers_api.base_url) as router:
        yield router
