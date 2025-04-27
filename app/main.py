# app/main.py

from fastapi import FastAPI

from middleware.telegram_user import TelegramUserMiddleware
from utils.logging_config import setup_logging
from utils.logging_middleware import LoggingMiddleware

from api.routes import api_router

setup_logging()
app = FastAPI()
app.add_middleware(LoggingMiddleware)
app.add_middleware(TelegramUserMiddleware)
app.include_router(api_router)


@app.get("/")
def health_check():
    return {"status": "ok"}
