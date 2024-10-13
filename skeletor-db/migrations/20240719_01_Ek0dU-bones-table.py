"""
Создает таблицу bones.
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS bones (
            id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            kind TEXT NOT NULL,
            owner_id BIGINT NOT NULL,
            size REAL NOT NULL
        );
        """,
        """
        DROP TABLE IF EXISTS bones;
        """
    )
]
