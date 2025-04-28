# app/tests/test_routes.py
import pytest


@pytest.mark.asyncio
async def test_unauthorized_endpoints(async_client, route_data1):
    """
    Without a token, all protected handles should return 401 Unauthorized.
    """
    # POST /routes/
    r = await async_client.post("/routes/", json=route_data1)
    assert r.status_code == 401

    # GET /routes/
    r = await async_client.get("/routes/")
    assert r.status_code == 401

    # GET /routes/{id}
    r = await async_client.get("/routes/1")
    assert r.status_code == 401

    # PUT /routes/{id}
    r = await async_client.put("/routes/1", json=route_data1)
    assert r.status_code == 401

    # DELETE /routes/{id}
    r = await async_client.delete("/routes/1")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_get_list_by_id_and_code(async_client, auth_headers, route_data1):
    # 1) CREATE
    resp = await async_client.post("/routes/", json=route_data1, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    created = resp.json()
    assert created["origin"] == "Paris"
    route_id = created["id"]
    share_code = created["share_code"]

    # attributes RouteShort
    assert created["origin"] == route_data1["origin"]
    assert created["destination"] == route_data1["destination"]
    assert created["duration_days"] == route_data1["duration_days"]
    assert created["budget"] == route_data1["budget"]

    # 2) GET by ID (requires token)
    resp2 = await async_client.get(f"/routes/{route_id}", headers=auth_headers)
    assert resp2.status_code == 200, resp2.text
    got = resp2.json()
    assert got["id"] == route_id
    assert got["origin"] == route_data1["origin"]
    # RouteRead has days
    assert "days" in got and isinstance(got["days"], list)

    # 3) LIST all for user
    resp3 = await async_client.get("/routes/", headers=auth_headers)
    assert resp3.status_code == 200
    lst = resp3.json()
    assert isinstance(lst, list)
    assert any(r["id"] == route_id for r in lst)

    # 4) GET by share_code (not requires token)
    resp4 = await async_client.get(f"/routes/by_code/{share_code}")
    assert resp4.status_code == 200
    bycode = resp4.json()
    assert bycode["id"] == route_id
    assert bycode["share_code"] == share_code


@pytest.mark.asyncio
async def test_get_routes_by_owner(async_client, auth_headers, route_data1):
    """
    GET /routes/by_owner/{owner_id}:
    - successful for owner_id
    - 403 for another user_id
    """
    # create route
    r = await async_client.post("/routes/", json=route_data1, headers=auth_headers)
    assert r.status_code == 201
    route = r.json()

    # get full model to get owner_id
    full = await async_client.get(f"/routes/{route['id']}", headers=auth_headers)
    owner_id = full.json()["owner_id"]

    # 1) success - owner_id
    ok = await async_client.get(f"/routes/by_owner/{owner_id}", headers=auth_headers)
    assert ok.status_code == 200
    arr = ok.json()
    assert any(r0["id"] == route["id"] for r0 in arr)

    # 2) not success - another user_id
    forbidden = await async_client.get(f"/routes/by_owner/{owner_id + 1}", headers=auth_headers)
    assert forbidden.status_code == 403


@pytest.mark.asyncio
async def test_rebuild_and_delete(async_client, auth_headers, route_data1, route_data2):
    """
    PUT /routes/{id} changes route,
    DELETE /routes/{id} deletes route.
    !!! routes can only be taken from ai_cache at the moment !!!
    """
    # create route
    create = await async_client.post("/routes/", json=route_data1, headers=auth_headers)
    assert create.status_code == 201
    r0 = create.json()
    rid = r0["id"]

    # rebuild route
    new = route_data2
    rebuild = await async_client.put(f"/routes/{rid}", json=new, headers=auth_headers)
    assert rebuild.status_code == 200, rebuild.text
    rb = rebuild.json()
    assert rb["id"] == rid + 1
    assert rb["budget"] == new["budget"]

    # delete route
    delete = await async_client.delete(f"/routes/{rb["id"]}", headers=auth_headers)
    assert delete.status_code == 204

    # after delete GET should return 403
    missing = await async_client.get(f"/routes/{rb["id"]}", headers=auth_headers)
    assert missing.status_code == 403
