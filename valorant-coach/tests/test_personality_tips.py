import pytest
from httpx import ASGITransport, AsyncClient

from src.app import app

BASE_PAYLOAD = {
    "map_name": "Ascent",
    "agent": "Sova",
    "econ": "full",
    "kda": "10/5/2",
    "first_duels_taken": 10,
    "first_duels_won": 6,
    "abilities_used_pct": 90,
    "deaths_while_entrying": 0,
    "favorite_weapon": "Vandal",
    # removed plants/defuses/rounds to match simplified input set
}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "personality, expected_keyword",
    [
        ("strict", "Fix:"),
        ("chill", "Keep it chill"),
        ("analyst", "Analysis:"),
    ],
)
async def test_personality_default_tip(personality, expected_keyword):
    transport = ASGITransport(app=app)
    payload = dict(BASE_PAYLOAD)
    payload["personality"] = personality
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/coach", json=payload)
    assert r.status_code == 200
    data = r.json()
    tips = data.get("tips") or []
    # Ensure at least one tip and that the personality tone appears in the messages
    assert len(tips) >= 1
    combined = " ".join(t.get("message", "") for t in tips)
    assert expected_keyword in combined
