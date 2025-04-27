import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_route(client: AsyncClient, auth_headers):
    payload = {
        "origin": "Berlin",
        "destination": "Berlin",
        "duration_days": 3,
        "budget": 1200,
        "interests": ["culture", "history"],
        "is_public": False,
    }
    response = await client.post("/routes/", json=payload, headers=auth_headers)

    print(response.json())

    assert response.status_code == 201
    data = response.json()
    assert data["origin"] == "Berlin"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_routes(client: AsyncClient, auth_headers):
    response = await client.get("/routes/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
