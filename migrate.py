from typer import Argument, Option, Typer
from yoyo import get_backend, read_migrations  # type: ignore[import-untyped]

app = Typer()


@app.command(help="Run local database migrations")
def main(
    db_url: str = Argument(envvar="DB_URL"),
    migrations_dir: str = Option(default="users-db/migrations"),
) -> None:
    db = get_backend(db_url)
    migrations = read_migrations(migrations_dir)

    with db.lock():
        db.apply_migrations(db.to_apply(migrations))


if __name__ == "__main__":
    app()
