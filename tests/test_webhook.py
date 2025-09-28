import pytest, hmac, hashlib, json
from httpx import AsyncClient
from app.main import app
from app import config
@pytest.mark.asyncio
async def test_webhook_bad_sig():
    payload = {"zen": "Keep it logically awesome."}
    body = json.dumps(payload).encode("utf-8")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/webhook", content=body, headers={
            "X-GitHub-Event": "ping",
            "X-Hub-Signature-256": "sha256=deadbeef"
        })
    assert r.status_code == 401
@pytest.mark.asyncio
async def test_webhook_ok_sig(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET", "s3cr3t")
    from importlib import reload
    reload(config)
    payload = {"zen": "Keep it logically awesome.", "action": "ping"}
    body = json.dumps(payload).encode("utf-8")
    mac = hmac.new(b"s3cr3t", body, hashlib.sha256).hexdigest()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/webhook", content=body, headers={
            "X-GitHub-Event": "ping",
            "X-Hub-Signature-256": f"sha256={mac}",
            "X-GitHub-Delivery": "delivery-1"
        })
    assert r.status_code == 204
