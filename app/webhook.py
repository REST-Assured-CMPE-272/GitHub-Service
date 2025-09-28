#Author : Atharva Kulkarni
import hmac, hashlib, json, os, time
from fastapi import HTTPException
EVENTS_FILE = "events.jsonl"
INDEX_FILE = "events_index.json"

def _load_index():
    if not os.path.exists(INDEX_FILE): return {}
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return {}

def _save_index(index): 
    with open(INDEX_FILE, "w", encoding="utf-8") as f: json.dump(index, f)

def verify_signature(secret: str, payload: bytes, signature_header: str):
    if not signature_header or not signature_header.startswith("sha256="):
        raise HTTPException(status_code=401, detail="missing or invalid signature")
    sig = signature_header.split("=", 1)[1]
    mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(mac, sig):
        raise HTTPException(status_code=401, detail="signature mismatch")
    
def store_event(delivery_id: str, event: str, action: str, issue_number: int|None):
    key = f"{delivery_id}:{action}"
    index = _load_index()
    if index.get(key): return False
    record = {
        "id": delivery_id, "event": event, "action": action,
        "issue_number": issue_number, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    with open(EVENTS_FILE, "a", encoding="utf-8") as f: f.write(json.dumps(record) + "\n")
    index[key] = True; _save_index(index); return True

def read_events(limit: int = 25):
    if not os.path.exists(EVENTS_FILE): return []
    lines = []
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip(): lines.append(json.loads(line))
    return list(reversed(lines))[:limit]
