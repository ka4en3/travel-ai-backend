# app/tests/test_route_access.py

import pytest


@pytest.mark.asyncio
async def test_route_access_flow(async_client, auth_headers, route_data1):
    # 1) create route and get share code for creator (CREATOR)
    cr = await async_client.post("/routes/", json=route_data1, headers=auth_headers)
    assert cr.status_code == 201, cr.text
    j = cr.json()
    rid = j["id"]
    share_code = j["share_code"]

    # 2) register and login user2
    reg2 = {"email": "u2@example.com", "password": "pass2"}
    await async_client.post("/auth/register", json=reg2)
    lg = {"username": reg2["email"], "password": reg2["password"]}
    tok2 = (await async_client.post("/auth/login", data=lg)).json()["access_token"]
    h2 = {"Authorization": f"Bearer {tok2}"}

    # 3) first user can get route by share code
    r0 = await async_client.get(f"/route-access/{rid}/get-share-code", headers=auth_headers)
    assert r0.status_code == 200
    # second user can't get route by share code → 403
    r0 = await async_client.get(f"/route-access/{rid}/get-share-code", headers=h2)
    assert r0.status_code == 403

    # 4) accept-by-code → grant VIEWER
    r1 = await async_client.post("/route-access/accept-by-code", json={"code": share_code}, headers=h2)
    assert r1.status_code == 200, r1.text
    a = r1.json()
    assert a["role"] == "viewer" and a["route_id"] == rid

    # 5) double accept-by-code → 409
    r1b = await async_client.post("/route-access/accept-by-code", json={"code": share_code}, headers=h2)
    assert r1b.status_code == 409

    # 6) CREATOR grant EDITOR access to second user
    ge = await async_client.post(
        f"/route-access/{rid}/grant-editor", json={"target_user_id": a["user_id"]}, headers=auth_headers
    )
    assert ge.status_code == 200

    # 7) now second user can get share code
    r2 = await async_client.get(f"/route-access/{rid}/get-share-code", headers=h2)
    assert r2.status_code == 200
    assert r2.json()["share_code"] == share_code

    # 8) Viewer (second) can't grant EDITOR access → 403
    bad = await async_client.post(
        f"/route-access/{rid}/grant-editor", json={"target_user_id": a["user_id"]}, headers=h2
    )
    assert bad.status_code == 403

    # 9) Revoke ACCESS
    rev = await async_client.request(
        "DELETE",
        f"/route-access/{rid}/revoke-access",
        json={"target_user_id": a["user_id"]},
        headers=auth_headers,
    )
    assert rev.status_code == 200

    # 10) After revoke second user can't get share code again
    r3 = await async_client.get(f"/route-access/{rid}/get-share-code", headers=h2)
    assert r3.status_code == 403
