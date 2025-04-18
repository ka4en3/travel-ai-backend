# app/main.py

from fastapi import FastAPI
from utils.logging_config import setup_logging
from utils.logging_middleware import LoggingMiddleware

from api.routes import api_router

setup_logging()
app = FastAPI()
app.add_middleware(LoggingMiddleware)
app.include_router(api_router)


@app.get("/")
def health_check():
    return {"status": "ok"}
