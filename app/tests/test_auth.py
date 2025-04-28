# app/tests/test_auth.py

import pytest


@pytest.mark.asyncio
async def test_register_and_login(async_client):
    # registration new user
    payload = {"email": "new@example.com", "password": "strongpass"}
    resp = await async_client.post("/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["email"] == payload["email"]
    assert "id" in data

    # registration already registered user → 409
    resp2 = await async_client.post("/auth/register", json=payload)
    assert resp2.status_code == 409

    # successful login
    login_data = {"username": payload["email"], "password": payload["password"]}
    resp3 = await async_client.post("/auth/login", data=login_data)
    assert resp3.status_code == 200, resp3.text
    tok = resp3.json()
    assert tok["token_type"] == "bearer"
    assert "access_token" in tok

    # wrong password
    bad = {"username": payload["email"], "password": "wrong"}
    resp4 = await async_client.post("/auth/login", data=bad)
    assert resp4.status_code == 401
