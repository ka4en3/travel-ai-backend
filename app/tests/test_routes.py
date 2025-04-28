import pytest


@pytest.mark.asyncio
async def test_create_route(async_client, auth_headers, route_data):
    response = await async_client.post("/routes/", json=route_data, headers=await auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["origin"] == "Paris"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_routes(async_client, auth_headers):
    response = await async_client.get("/routes/", headers=await auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
