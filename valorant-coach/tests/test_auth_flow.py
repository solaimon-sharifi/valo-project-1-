import uuid

import pytest
from httpx import ASGITransport, AsyncClient

PASSWORD = "P@ssw0rd"


@pytest.mark.asyncio
async def test_register_creates_session(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        username = f"register-{uuid.uuid4().hex[:6]}"
        resp = await ac.post(
            "/register",
            data={"username": username, "password": PASSWORD},
            follow_redirects=False,
        )
    assert resp.status_code == 303
    assert resp.headers.get("location") == "/dashboard/app"
    assert "access_token" in ac.cookies


@pytest.mark.asyncio
async def test_login_and_protected_dashboards(app):
    transport = ASGITransport(app=app)
    username = f"login-{uuid.uuid4().hex[:6]}"
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post(
            "/register",
            data={"username": username, "password": PASSWORD},
            follow_redirects=False,
        )
        ac.cookies.clear()
        login_resp = await ac.post(
            "/login",
            data={"username": username, "password": PASSWORD},
            follow_redirects=False,
        )
        assert login_resp.status_code == 303
        dashboard = await ac.get("/dashboard/app")
        valorant = await ac.get("/valorant-dashboard")
    assert dashboard.status_code == 200
    assert valorant.status_code == 200


@pytest.mark.asyncio
async def test_dashboard_redirects_when_unauthenticated(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/dashboard/app", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers.get("location") == "/login"
