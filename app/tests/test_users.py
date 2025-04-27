# import pytest
# from httpx import AsyncClient
#
#
# @pytest.mark.asyncio
# async def test_get_or_create_user(async_client: AsyncClient):
#     data = {"email": "user1@example.com", "password": "password123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 201
#     assert response.json()["email"] == "user1@example.com"
#
#     response_dup = await async_client.post("/auth/register", json=data)
#     assert response_dup.status_code == 409  # duplicate registration should fail
#
#
# @pytest.mark.asyncio
# async def test_get_or_create_telegram_user(async_client: AsyncClient):
#     telegram_data = {
#         "telegram_id": 123456789,
#         "username": "test_telegram_user",
#         "first_name": "Test",
#         "last_name": "User",
#         "is_bot": False,
#         "is_premium": True,
#         "language": "en",
#     }
#     response = await async_client.post("/auth/telegram-login", json=telegram_data)
#     assert response.status_code == 201
#     print(response.json())
#     assert response.json()["telegram_id"] == 123456789
#
#     response_dup = await async_client.post("/auth/telegram-login", json=telegram_data)
#     assert response_dup.status_code == 200  # should return existing user
#
#
# @pytest.mark.asyncio
# async def test_telegram_user_not_duplicated(async_client: AsyncClient):
#     telegram_data = {
#         "telegram_id": 123456789,
#         "username": "test_telegram_user",
#         "first_name": "Test",
#         "last_name": "User",
#         "is_bot": False,
#         "is_premium": True,
#         "language": "en",
#     }
#
#     response_1 = await async_client.post("/auth/telegram-register", json=telegram_data)
#     assert response_1.status_code == 201
#
#     response_2 = await async_client.post("/auth/telegram-register", json=telegram_data)
#     assert response_2.status_code == 200
#
#     user_1 = response_1.json()
#     user_2 = response_2.json()
#
#     assert user_1["id"] == user_2["id"]
#     assert user_1["telegram_id"] == user_2["telegram_id"]
#
#
# @pytest.mark.asyncio
# async def test_get_current_user_from_token(async_client: AsyncClient):
#     register_data = {"username": "tokenuser@example.com", "password": "passtoken"}
#     await async_client.post("/auth/register", json=register_data)
#     login_res = await async_client.post("/auth/login", data=register_data)
#     token = login_res.json()["access_token"]
#     headers = {"Authorization": f"Bearer {token}"}
#
#     response = await async_client.get("/auth/me", headers=headers)
#     assert response.status_code == 200
#     user_data = response.json()
#     assert user_data["email"] == "tokenuser@example.com"
