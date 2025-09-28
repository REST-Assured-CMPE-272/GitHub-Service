from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import uuid, json, logging
from .logging import setup_logging
from . import config
from .models import CreateIssueRequest, UpdateIssueRequest, CreateCommentRequest, ErrorModel
from .pagination import forward_pagination_headers
from .webhook import verify_signature, store_event, read_events
from . import github
setup_logging()
logger = logging.getLogger("api")
app = FastAPI(title="GitHub Issues Gateway", version="1.0.0")

# Author : Atharva Kulkarni
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": str(e.detail)})
    response.headers["x-request-id"] = request_id
    return response

# Author : Atharva Kulkarni
def _issue_shape(raw: dict) -> dict:
    labels = [l["name"] for l in raw.get("labels", []) if isinstance(l, dict) and "name" in l]
    return {
        "number": raw.get("number"), "html_url": raw.get("html_url"),
        "state": raw.get("state"), "title": raw.get("title"),
        "body": raw.get("body"), "labels": labels,
        "created_at": raw.get("created_at"), "updated_at": raw.get("updated_at"),
    }

# Author : Atharva Kulkarni
@app.post("/issues", status_code=201, responses={400: {"model": ErrorModel}, 401: {"model": ErrorModel}})
async def create_issue(payload: CreateIssueRequest, response: Response):
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    data = payload.dict(exclude_none=True)
    created = await github.create_issue(data)
    response.headers["Location"] = f"/issues/{created['number']}"
    return _issue_shape(created)

# author : Shantanu Zadbuke
@app.post("/issues/{number}/comments", status_code=201)
async def create_comment(number: int, payload: CreateCommentRequest):
    if not payload.body or not payload.body.strip():
        raise HTTPException(status_code=400, detail="comment body is required")
    raw = await github.create_comment(number, payload.body)
    return { "id": raw.get("id"), "body": raw.get("body"),
             "user": {"login": raw.get("user", {}).get("login")},
             "created_at": raw.get("created_at"), "html_url": raw.get("html_url") }

# author : Shantanu Zadbuke
@app.get("/issues")
async def list_issues(state: str = "open", labels: Optional[str] = None, page: int = 1, per_page: int = 30, response: Response = None):
    if state not in ("open","closed","all"):
        raise HTTPException(status_code=400, detail="invalid state; must be one of: open, closed, all")
    if per_page < 1 or per_page > 100:
        raise HTTPException(status_code=400, detail="per_page must be 1..100")
    items, headers = await github.list_issues(state, labels, page, per_page)
    forward_pagination_headers(headers, response)
    return [_issue_shape(i) for i in items]

# author : Shantanu Zadbuke
@app.get("/issues/{number}")
async def get_issue(number: int):
    raw = await github.get_issue(number)
    return _issue_shape(raw)

# Author : Akshay Navani
@app.patch("/issues/{number}")
async def update_issue(number: int, payload: UpdateIssueRequest):
    if payload.state and payload.state not in ("open","closed"):
        raise HTTPException(status_code=400, detail="invalid state; must be open or closed")
    data = payload.dict(exclude_none=True)
    raw = await github.update_issue(number, data)
    return _issue_shape(raw)

@app.post("/webhook", status_code=204)
async def webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("x-hub-signature-256")
    event = request.headers.get("x-github-event")
    delivery_id = request.headers.get("x-github-delivery", str(uuid.uuid4()))
    if not event: raise HTTPException(status_code=400, detail="missing X-GitHub-Event")
    verify_signature(config.WEBHOOK_SECRET or "", body, sig)
    payload = json.loads(body.decode("utf-8"))
    action = payload.get("action", "")
    issue_number = payload.get("issue", {}).get("number") if isinstance(payload.get("issue"), dict) else None
    if event not in ("issues","issue_comment","ping"):
        raise HTTPException(status_code=400, detail=f"unsupported event: {event}")
    store_event(delivery_id, event, action, issue_number)
    return Response(status_code=204)

@app.get("/events")
async def events(limit: int = 25):
    return read_events(limit=limit)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}