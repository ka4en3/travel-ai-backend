import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(async_client):
    user_data = {"email": "newuser@example.com", "password": "newpassword"}
    response = await async_client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"

    login_data = {
        "username": user_data["email"],
        "password": user_data["password"],
    }
    response = await async_client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    response = await async_client.get("/auth/me", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_register_duplicate_user(async_client: AsyncClient):
    data = {"email": "newuser@example.com", "password": "newpassword"}
    response = await async_client.post("/auth/register", json=data)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient):
    data = {"username": "newuser@example.com", "password": "wrongpassword"}
    response = await async_client.post("/auth/login", data=data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_user(async_client: AsyncClient):
    data = {"username": "unknown@example.com", "password": "any"}
    response = await async_client.post("/auth/login", data=data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_access_protected_route_without_token(async_client: AsyncClient):
    response = await async_client.get("/routes/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_access_protected_route_with_invalid_token(async_client: AsyncClient):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await async_client.get("/routes/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_payload_contains_correct_fields(async_client: AsyncClient):
    login_data = {"username": "newuser@example.com", "password": "newpassword"}
    login_res = await async_client.post("/auth/login", data=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/auth/me", headers=headers)
    print(response.json())
    print(response.status_code)
    assert response.status_code == 200
    user_data = response.json()
    assert "id" in user_data
    assert "email" in user_data
