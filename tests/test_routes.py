import pytest
from httpx import AsyncClient
from app.main import app
@pytest.mark.asyncio
async def test_create_issue_validation():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/issues", json={"title": ""})
    assert r.status_code == 400
    assert "title" in r.json()["error"]
@pytest.mark.asyncio
async def test_update_issue_invalid_state():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.patch("/issues/1", json={"state": "invalid"})
    assert r.status_code == 400
