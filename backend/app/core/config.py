from pydantic import BaseSettings, Field

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class DatabaseSettings(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 5432
    USER: str = Field(..., env="POSTGRES_USER")
    PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    NAME: str = Field(..., env="POSTGRES_DB")
    echo: bool = False
    pool_size: int = 50
    max_overflow: int = 0

    @property
    def credentials(self) -> str:
        return f"{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self.credentials}"


class RedisSettings(BaseSettings):
    URL: str = Field(..., env="REDIS_URL")


class BotSettings(BaseSettings):
    TOKEN: str = Field(..., env="TELEGRAM_TOKEN")


class AISettings(BaseSettings):
    CHATGPT_API_KEY: str = Field(..., env="CHATGPT_API_KEY")


class APISettings(BaseSettings):
    HOST: str = Field("0.0.0.0", env="API_HOST")
    PORT: int = Field(8000, env="API_PORT")


class Settings(BaseSettings):
    db = DatabaseSettings()
    redis = RedisSettings()
    bot = BotSettings()
    ai = AISettings()
    api = APISettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def display(self):
        print("DATABASE:", self.db.async_url)
        print("REDIS:", self.redis.URL)
        print("BOT TOKEN:", "***" if self.bot.TOKEN else "None")
        print("CHATGPT KEY:", "***" if self.ai.CHATGPT_API_KEY else "None")


settings = Settings()
