from fastapi import HTTPException
def map_rate_limit(headers):
    remaining = headers.get("x-ratelimit-remaining")
    if remaining is not None and remaining == "0":
        retry_after = headers.get("retry-after")
        detail = "GitHub rate limit exceeded"
        if retry_after:
            detail += f"; retry after {retry_after}s"
        return HTTPException(status_code=429, detail=detail)
    return None
