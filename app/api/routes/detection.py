from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
import uuid

router = APIRouter()


class DetectionRequest(BaseModel):
    camera_id: str
    detected_count: int
    confidence: float


@router.post("")
def post_detection(body: DetectionRequest, db: Session = Depends(get_db)):
    db.execute(
        text("INSERT INTO detections (id, camera_id, detected_count, confidence) VALUES (:id, :camera_id, :detected_count, :confidence)"),
        {"id": str(uuid.uuid4()), "camera_id": body.camera_id, "detected_count": body.detected_count, "confidence": body.confidence}
    )
    db.commit()
    return {"success": True}


@router.get("/latest/{camera_id}")
def get_latest(camera_id: str, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT * FROM detections WHERE camera_id = :camera_id ORDER BY detected_at DESC LIMIT 1"),
        {"camera_id": camera_id}
    ).fetchone()
    if not row:
        return {"data": None}
    return {"data": dict(row._mapping)}
