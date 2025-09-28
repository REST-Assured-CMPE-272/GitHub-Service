from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
class CreateIssueRequest(BaseModel):
    title: str
    body: Optional[str] = None
    labels: Optional[List[str]] = None
class UpdateIssueRequest(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[str] = Field(None, pattern="^(open|closed)$")
class CreateCommentRequest(BaseModel):
    body: str
class ErrorModel(BaseModel):
    error: str
    details: Optional[Dict[str, Any]] = None
