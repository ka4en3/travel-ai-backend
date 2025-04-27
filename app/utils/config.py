# app/utils/config.py

import os
import logging
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy naming conventions for Alembic
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Settings(BaseSettings):
    # Database settings (match .env variable names exactly)
    POSTGRES_USER: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_DB: str = Field(...)
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432, ge=1)
    DB_ECHO: bool = Field(default=False)
    DB_POOL_SIZE: int = Field(
        default=50,
    )
    DB_MAX_OVERFLOW: int = Field(default=0)
    DB_CONNECT_TIMEOUT: int = Field(default=30)

    # Redis settings
    REDIS_URL: str = Field(...)

    # Bot settings
    TELEGRAM_TOKEN: str = Field(...)

    # AI settings
    CHATGPT_API_KEY: str = Field(...)

    # API settings
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000, ge=1, le=65535)

    # JWT
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 24, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # DEBUG
    DEBUG: bool = False

    class Config:
        env_file = os.getenv("ENV_FILE", ".env")
        env_file_encoding = "utf-8"

    # Database properties
    @property
    def db_credentials(self) -> str:
        return f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"

    @property
    def db_async_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_credentials}"

    # Validator for Redis URL
    @field_validator("REDIS_URL")
    def validate_redis_url(cls, v: str) -> str:
        if not v.startswith("redis://"):
            raise ValueError("Redis URL must start with 'redis://'")
        return v

    def display(self) -> None:
        """Display settings with masked sensitive data."""
        masked_db_url = self.db_async_url.replace(self.POSTGRES_PASSWORD, "***")
        logger.info("DATABASE: %s", masked_db_url)
        logger.info("REDIS: %s", self.REDIS_URL)
        logger.info("BOT TOKEN: %s", "***" if self.TELEGRAM_TOKEN else "None")
        logger.info("CHATGPT KEY: %s", "***" if self.CHATGPT_API_KEY else "None")


# Singleton instance with error handling
try:
    settings = Settings()
except ValidationError as e:
    logger.error("Configuration validation failed: %s", e)
    raise
except Exception as e:
    logger.error("Unexpected error during settings initialization: %s", e)
    raise

if __name__ == "__main__":
    settings.display()
