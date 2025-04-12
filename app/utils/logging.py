# app/core/logging.py

from logging.config import dictConfig


def setup_logging():
    dictConfig({
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
            "level": "INFO",
        },
        "loggers": {
            "app": {
                "handlers": ["default"],
                "level": "DEBUG",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "INFO",  # INFO or DEBUG to see SQL
            },
        },
    })
