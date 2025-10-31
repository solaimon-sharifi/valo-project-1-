import pytest
from httpx import AsyncClient, ASGITransport

from src.app import app


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/", headers={"accept": "application/json"})
    assert r.status_code == 200
    assert r.json().get("ok") is True


@pytest.mark.asyncio
async def test_coach_endpoint():
    payload = {
        "map_name": "Ascent",
        "agent": "Sova",
        "econ": "full",
        "kda": "16/14/3",
        "first_duels_taken": 10,
        "first_duels_won": 3,
        "abilities_used_pct": 55,
        "plants": 2,
        "defuses": 1,
        "avg_time_to_engage_ms": 23000,
        "deaths_while_entrying": 6,
        "favorite_weapon": "Vandal",
        "rounds_played": 20,
        "personality": "analyst",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/coach", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("tips"), list) and len(data["tips"]) >= 1
    assert "win_rate" in data["metrics"]
    assert "kd_ratio" in data["metrics"]


@pytest.mark.asyncio
async def test_metrics_and_heatmap():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        m = await ac.get("/metrics/demo")
        h = await ac.get("/heatmap/demo")
    assert m.status_code == 200
    assert "win_rate" in m.json()
    assert h.status_code == 200
    assert isinstance(h.json().get("hotspots"), list)
