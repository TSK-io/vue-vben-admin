import logging
from logging.config import dictConfig

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
                },
                "plain": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json" if settings.app_env == "production" else "plain",
                }
            },
            "root": {
                "handlers": ["console"],
                "level": settings.app_log_level.upper(),
            },
        }
    )
    logging.getLogger("uvicorn.access").handlers = []
