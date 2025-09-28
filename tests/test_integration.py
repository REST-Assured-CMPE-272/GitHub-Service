import os, pytest
from httpx import AsyncClient
from app.main import app
run_integration = os.getenv("RUN_INTEGRATION") == "1"
pytestmark = pytest.mark.skipif(not run_integration, reason="set RUN_INTEGRATION=1 with valid env vars")
@pytest.mark.asyncio
async def test_crud_and_comment():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/issues", json={"title": "HW2 test issue", "body": "created by integration test"})
        assert r.status_code == 201, r.text
        num = r.json()["number"]
        r = await ac.get(f"/issues/{num}"); assert r.status_code == 200
        r = await ac.patch(f"/issues/{num}", json={"title": "HW2 test issue (edited)"}); assert r.status_code == 200
        r = await ac.patch(f"/issues/{num}", json={"state": "closed"}); assert r.status_code == 200
        r = await ac.patch(f"/issues/{num}", json={"state": "open"}); assert r.status_code == 200
        r = await ac.post(f"/issues/{num}/comments", json={"body": "integration comment"}); assert r.status_code == 201
