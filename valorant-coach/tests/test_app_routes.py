import uuid

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_root_serves_index(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", headers={"accept": "text/html"}
    ) as ac:
        resp = await ac.get("/")
    assert resp.status_code == 200
    assert "Valorant Tactical Coach" in resp.text
    assert "text/html" in resp.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_login_form_renders_template(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/login")
    assert resp.status_code == 200
    assert "<h1>Login</h1>" in resp.text


@pytest.mark.asyncio
async def test_login_invalid_credentials_shows_message(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/login",
            data={"username": "missing-user", "password": "nopassword"},
        )
    assert resp.status_code == 200
    assert "Invalid username or password." in resp.text


@pytest.mark.asyncio
async def test_register_form_renders_template(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/register")
    assert resp.status_code == 200
    assert "<h1>Register</h1>" in resp.text


@pytest.mark.asyncio
async def test_register_missing_fields_returns_message(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/register", data={"username": "", "password": ""})
    assert resp.status_code == 200
    assert "Enter both username and password." in resp.text


@pytest.mark.asyncio
async def test_register_existing_user_returns_message(app):
    username = f"dup-{uuid.uuid4().hex[:6]}"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post(
            "/register",
            data={"username": username, "password": "valid123"},
            follow_redirects=False,
        )
        resp = await ac.post(
            "/register",
            data={"username": username, "password": "valid123"},
        )
    assert resp.status_code == 200
    assert "Username already exists." in resp.text


@pytest.mark.asyncio
async def test_dashboard_redirects_to_app(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/dashboard", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers.get("location") == "/dashboard/app"


@pytest.mark.asyncio
async def test_valorant_dashboard_without_token_redirects(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/valorant-dashboard", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers.get("location") == "/login"


@pytest.mark.asyncio
async def test_dashboard_with_invalid_token_redirects(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.cookies.set("access_token", "Bearer invalid-token")
        resp = await ac.get("/dashboard/app", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers.get("location") == "/login"


@pytest.mark.asyncio
async def test_logout_clears_cookie(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/logout", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers.get("location") == "/"
    set_cookie = resp.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie
