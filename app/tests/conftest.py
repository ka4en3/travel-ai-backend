import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pytest_asyncio
from httpx import AsyncClient


os.environ["POSTGRES_USER"] = "admin"
os.environ["POSTGRES_PASSWORD"] = "password"
os.environ["POSTGRES_DB"] = "travel_ai_db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["TELEGRAM_TOKEN"] = "test_telegram_token"
os.environ["CHATGPT_API_KEY"] = "test_chatgpt_key"
os.environ["JWT_SECRET_KEY"] = "some-very-secret-value"

from utils.security import create_access_token
from db.sessions import async_session_factory, get_session
from repositories.user import UserRepository
from services.crud.user_service import UserService
from schemas.user import UserCreate


# ---------- Test client fixture ---------- #
@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        yield ac


# ---------- Async DB session fixture ---------- #
@pytest_asyncio.fixture
async def async_session():
    async for session in get_session():
        yield session


# ---------- Create test user fixture ---------- #
@pytest_asyncio.fixture
async def test_user(async_session):
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
def auth_headers(test_user):
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
