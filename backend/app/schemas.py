from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class DetectRequest(BaseModel):
    sample_id: Optional[str]
    timestamp: Optional[str]
    detection: Dict[str, Any]


class DetectResponse(BaseModel):
    report_id: str
    summary: Dict[str, Any]
    report_path: str


class PublishRequest(BaseModel):
    report_id: str
    order_token: Optional[str]
