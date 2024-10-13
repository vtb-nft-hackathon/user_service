import logging
import logging.config
from asyncio import CancelledError
from logging.handlers import QueueHandler, QueueListener
from queue import SimpleQueue
from typing import Any

from app.core.settings import Config, Environments


def setup_log_parameters(config: Config) -> None:
    _, logs_config = create_logs_parameters(config=config)

    logging.config.dictConfig(logs_config)


def create_logs_parameters(config: Config) -> tuple[str, dict[str, Any]]:
    formatter = "verbose" if config.environment == Environments.local else "json"
    level_name = logging.getLevelName(logging.DEBUG if config.debug else logging.INFO)

    params = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "class": "logging.Formatter",
                "format": "%(asctime)s.%(msecs)03d [%(process)d] "
                "[%(name)s:%(module)s:%(funcName)s:%(lineno)d] %(levelname)s: "
                "%(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            # TODO: если раскомментить - ошибка при конфигурации логгера. Потом разобраться почему # noqa: TD002 TD003 FIX002 E501 RUF100
            # "json": { # noqa: ERA001
            #     "class": "json_formatter.JsonFormatter", # noqa: ERA001 RUF100
            #     "format": "%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s " # noqa: ERA001 RUF100
            #     "%(lineno)d %(message)s %(stack_trace)s", # noqa: ERA001 RUF100
            #     "datefmt": "%Y-%m-%d %H:%M:%S", # noqa: ERA001 RUF100
            # }, # noqa: ERA001 RUF100
        },
        "handlers": {
            "console": {
                "level": level_name,
                "class": "logging.StreamHandler",
                "formatter": formatter,
            },
        },
        "loggers": {
            "root": {
                "handlers": ["console"],
                "level": level_name,
            },
            "app": {
                "handlers": ["console"],
                "propagate": False,
                "level": level_name,
            },
        },
    }
    lower_level_name = level_name.lower()

    return lower_level_name, params


class CustomQueueHandler(QueueHandler):
    def emit(self, record: logging.LogRecord) -> None:
        # Removed the call to self.prepare(), handle task cancellation
        try:
            self.enqueue(record)
        except CancelledError:
            raise
        except Exception:  # noqa: BLE001
            self.handleError(record)


def start_async_logging() -> QueueListener:
    log_queue: SimpleQueue[logging.LogRecord] = SimpleQueue()
    root_logger = logging.getLogger()

    handlers = []

    handler = CustomQueueHandler(log_queue)
    root_logger.addHandler(handler)
    for h in root_logger.handlers:
        if h is not handler:
            root_logger.removeHandler(h)
            handlers.append(h)

    listener = QueueListener(log_queue, *handlers, respect_handler_level=True)
    listener.start()

    logging.info("Loggers have started")
    return listener


def stop_async_logging(logging_listener: QueueListener) -> None:
    logging_listener.stop()
    logging.info("Loggers have stopped")
