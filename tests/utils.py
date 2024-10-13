import json
from pathlib import Path
from typing import Any

TEST_BASE_PATH = Path(__file__).resolve().parent


def load_json(path: str) -> Any:
    """Загрузка данных из json файла."""
    with open(TEST_BASE_PATH / path) as f:
        return json.load(f)


def load_binary_file(path: str) -> bytes:
    """Загрузка бинарных данных из файла."""
    with open(TEST_BASE_PATH / path, "rb") as f:
        return f.read()


def load_text_file(path: str) -> str:
    """Загрузка текстовых данных из файла."""
    with open(TEST_BASE_PATH / path) as f:
        return f.read()
