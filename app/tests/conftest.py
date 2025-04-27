import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pytest_asyncio
from httpx import AsyncClient


os.environ["POSTGRES_USER"] = "test_user"
os.environ["POSTGRES_PASSWORD"] = "test_pass"
os.environ["POSTGRES_DB"] = "test_db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["TELEGRAM_TOKEN"] = "test_telegram_token"
os.environ["CHATGPT_API_KEY"] = "test_chatgpt_key"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret"

from utils.security import create_access_token
from db.sessions import async_session_factory
from repositories.user import UserRepository
from services.crud.user_service import UserService
from schemas.user import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession


# ---------- Test client fixture ---------- #
@pytest_asyncio.fixture
async def client():
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        yield ac


@pytest.fixture(scope="session")
def event_loop():
    import asyncio

    return asyncio.get_event_loop()


# ---------- Async DB session fixture ---------- #
@pytest.fixture
async def async_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
        await session.rollback()  # safety rollback after each test


# ---------- Create test user fixture ---------- #
@pytest.fixture
async def test_user(async_session: AsyncSession):
    user_repo = UserRepository(async_session)
    user_service = UserService(user_repo)
    user_data = UserCreate(email="testuser@example.com", password="testpassword")
    try:
        user = await user_service.register(user_data)
    except Exception:
        user = await user_repo.get_by_email(user_data.email)
    return user


# ---------- JWT token headers fixture ---------- #
@pytest.fixture
async def auth_headers(test_user):
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def route_data():
    return {
        "origin": "Paris",
        "destination": "Paris",
        "duration_days": 3,
        "budget": 1500.0,
        "interests": ["culture", "food"],
        "is_public": False,
    }
