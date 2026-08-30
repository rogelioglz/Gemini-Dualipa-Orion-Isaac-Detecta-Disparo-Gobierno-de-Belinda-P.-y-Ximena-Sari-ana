from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import uuid
from .processor import process_detection, get_report_path, publish_words_for_report

API_KEY = os.getenv("API_KEY", "dev-secret")
STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")

app = FastAPI(title="Gemini Sound Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")


class DetectRequest(BaseModel):
    sample_id: Optional[str]
    timestamp: Optional[str]
    detection: dict


class DetectResponse(BaseModel):
    report_id: str
    summary: dict
    report_path: str


@app.post("/api/detect", response_model=DetectResponse)
async def detect_endpoint(req: DetectRequest, x_api_key: Optional[str] = Header(None)):
    require_api_key(x_api_key)

    sample_id = req.sample_id or str(uuid.uuid4())
    report_id, summary, report_path = process_detection(sample_id, req.detection)
    return DetectResponse(report_id=report_id, summary=summary, report_path=report_path)


@app.get("/api/reports/{report_id}")
async def get_report(report_id: str, x_api_key: Optional[str] = Header(None)):
    require_api_key(x_api_key)
    path = get_report_path(report_id)
    if not path:
        raise HTTPException(status_code=404, detail="Report not found")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"report_id": report_id, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/publish/{report_id}")
async def publish_report(report_id: str, x_api_key: Optional[str] = Header(None)):
    require_api_key(x_api_key)
    published = publish_words_for_report(report_id)
    if not published:
        raise HTTPException(status_code=404, detail="Nothing to publish or report not found")
    return {"published_file": published}
