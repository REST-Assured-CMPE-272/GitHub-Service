#Author : Atharva Kulkarni
import logging, json, time
class JsonFormatter(logging.Formatter):
    def format(self, record):
        base = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": record.levelname, "msg": record.getMessage(), "logger": record.name
        }
        if hasattr(record, "request_id"): base["request_id"] = getattr(record, "request_id")
        if hasattr(record, "delivery_id"): base["delivery_id"] = getattr(record, "delivery_id")
        return json.dumps(base)
def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]
