# app/utils/logging.py

from logging.config import dictConfig
from utils.config import settings

LOG_LEVEL = "DEBUG" if settings.DEBUG else "INFO"


def setup_logging():
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s [%(asctime)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "handlers": ["default"],
                "level": LOG_LEVEL,
            },
            "loggers": {
                "app": {
                    "handlers": ["default"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                "app.repositories": {
                    "handlers": ["default"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                "app.services": {
                    "handlers": ["default"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                "sqlalchemy.engine": {
                    "level": LOG_LEVEL,
                    "handlers": ["default"],
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["default"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["default"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
            },
        }
    )
