from typing import Dict, Any, Optional, Tuple
import httpx
from fastapi import HTTPException
from . import config
from .rate_limit import map_rate_limit
ACCEPT = "application/vnd.github+json"
BASE = "https://api.github.com"
_etag_cache: Dict[Tuple[str, str, int, int], str] = {}
def _owner_repo() -> Tuple[str, str]:
    if not config.GITHUB_OWNER or not config.GITHUB_REPO:
        raise HTTPException(status_code=500, detail="GITHUB_OWNER and GITHUB_REPO must be set")
    return config.GITHUB_OWNER, config.GITHUB_REPO
def _auth_headers() -> Dict[str, str]:
    if not config.GITHUB_TOKEN:
        raise HTTPException(status_code=401, detail="missing GITHUB_TOKEN")
    return {"Authorization": f"Bearer {config.GITHUB_TOKEN}", "Accept": ACCEPT}
async def create_issue(data: Dict[str, Any]) -> Dict[str, Any]:
    owner, repo = _owner_repo()
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{BASE}/repos/{owner}/{repo}/issues", headers=_auth_headers(), json=data)
    if rate_exc := map_rate_limit(r.headers): raise rate_exc
    if r.status_code in (401,403): raise HTTPException(status_code=401, detail=r.text)
    if r.status_code >= 400: raise HTTPException(status_code=400, detail=r.text)
    return r.json()
async def list_issues(state: str, labels: Optional[str], page: int, per_page: int):
    owner, repo = _owner_repo()
    params = {"state": state, "page": page, "per_page": per_page}
    if labels: params["labels"] = labels
    headers = _auth_headers()
    key = (state, labels or "", page, per_page)
    if key in _etag_cache: headers["If-None-Match"] = _etag_cache[key]
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{BASE}/repos/{owner}/{repo}/issues", headers=headers, params=params)
    if rate_exc := map_rate_limit(r.headers): raise rate_exc
    if r.status_code == 304: raise HTTPException(status_code=304, detail="cached")
    etag = r.headers.get("etag"); 
    if etag: _etag_cache[key] = etag
    if r.status_code >= 400:
        if r.status_code in (401,403): raise HTTPException(status_code=401, detail=r.text)
        if r.status_code == 404: raise HTTPException(status_code=404, detail="not found")
        raise HTTPException(status_code=400, detail=r.text)
    return r.json(), dict(r.headers)
async def get_issue(number: int) -> Dict[str, Any]:
    owner, repo = _owner_repo()
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{BASE}/repos/{owner}/{repo}/issues/{number}", headers=_auth_headers())
    if rate_exc := map_rate_limit(r.headers): raise rate_exc
    if r.status_code == 404: raise HTTPException(status_code=404, detail="not found")
    if r.status_code in (401,403): raise HTTPException(status_code=401, detail=r.text)
    if r.status_code >= 400: raise HTTPException(status_code=400, detail=r.text)
    return r.json()
async def update_issue(number: int, data: Dict[str, Any]) -> Dict[str, Any]:
    owner, repo = _owner_repo()
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.patch(f"{BASE}/repos/{owner}/{repo}/issues/{number}", headers=_auth_headers(), json=data)
    if rate_exc := map_rate_limit(r.headers): raise rate_exc
    if r.status_code == 404: raise HTTPException(status_code=404, detail="not found")
    if r.status_code in (401,403): raise HTTPException(status_code=401, detail=r.text)
    if r.status_code >= 400: raise HTTPException(status_code=400, detail=r.text)
    return r.json()
async def create_comment(number: int, body: str) -> Dict[str, Any]:
    owner, repo = _owner_repo()
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{BASE}/repos/{owner}/{repo}/issues/{number}/comments",
                              headers=_auth_headers(), json={"body": body})
    if rate_exc := map_rate_limit(r.headers): raise rate_exc
    if r.status_code == 404: raise HTTPException(status_code=404, detail="not found")
    if r.status_code in (401,403): raise HTTPException(status_code=401, detail=r.text)
    if r.status_code >= 400: raise HTTPException(status_code=400, detail=r.text)
    return r.json()
