# app/tests/conftest.py

import os
import sys
import pytest, pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# add project root for correct imports
sys.path.append(str(os.path.dirname(os.path.dirname(__file__))))

# install test ENV
os.environ["POSTGRES_USER"] = "admin"
os.environ["POSTGRES_PASSWORD"] = "password"
os.environ["POSTGRES_DB"] = "travel_ai_db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["TELEGRAM_TOKEN"] = "test_telegram_token"
os.environ["CHATGPT_API_KEY"] = "test_chatgpt_key"
os.environ["JWT_SECRET_KEY"] = "some-very-secret-value"

from main import app as fastapi_app
from db.base_class import Base
from db.sessions import get_session
import fixtures.load_with_services as seed_mod

# create an engine and sessionmaker for SQLite in-memory
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# override the get_session dependency in the application
async def override_get_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session


fastapi_app.dependency_overrides[get_session] = override_get_session


# fixture to create all tables before any test
@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_db():
    # create scheme
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # seed data
    seed_mod.async_session_factory = TestingSessionLocal
    await seed_mod.load_all()

    yield

    # delete after
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# an asynchronous HTTP client that will “hook” into app
# @pytest_asyncio.fixture
@pytest_asyncio.fixture(scope="session")
async def async_client():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


# get JWT headers via API: register + log in
# @pytest_asyncio.fixture
@pytest_asyncio.fixture(scope="session")
async def auth_headers(async_client: AsyncClient):
    # register a new user through /auth/register
    register_payload = {"email": "test@example.com", "password": "secret"}
    r = await async_client.post("/auth/register", json=register_payload)
    assert r.status_code == 201, f"Registration failed: {r.text}"

    # do login via OAuth2PasswordRequestForm (/auth/login)
    form = {
        "username": register_payload["email"],  # OAuth2PasswordRequestForm.username == email
        "password": register_payload["password"],
    }
    r2 = await async_client.post("/auth/login", data=form)
    assert r2.status_code == 200, f"Login failed: {r2.text}"
    token = r2.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def route_data1():
    return {
        "origin": "Paris",
        "destination": "Paris",
        "duration_days": 3,
        "budget": 1500.0,
        "interests": ["culture", "history"],
        "is_public": False,
    }


@pytest.fixture
def route_data2():
    return {
        "origin": "Tokyo",
        "destination": "Tokyo",
        "duration_days": 5,
        "budget": 2500.0,
        "interests": ["technology", "anime", "gaming"],
        "is_public": False,
    }
