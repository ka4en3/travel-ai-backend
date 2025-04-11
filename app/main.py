# app/main.py

from fastapi import FastAPI
from core.logging import setup_logging
from core.logging_middleware import LoggingMiddleware

setup_logging()
app = FastAPI()
app.add_middleware(LoggingMiddleware)


@app.get("/")
def health_check():
    return {"status": "ok"}
