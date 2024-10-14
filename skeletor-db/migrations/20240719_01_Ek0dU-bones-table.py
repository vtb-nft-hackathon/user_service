"""
Создает таблицу wallet.
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS wallet (
            id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            user_id BIGINT NOT NULL,
            address text NOT NULL,
            private text NOT NULL
        );
        """,
        """
        DROP TABLE IF EXISTS wallet;
        """
    )
]
