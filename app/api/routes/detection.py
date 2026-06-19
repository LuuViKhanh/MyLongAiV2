from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db

router = APIRouter()


@router.get("/latest/{camera_id}")
def get_latest(camera_id: str, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT * FROM detections WHERE camera_id = :camera_id ORDER BY detected_at DESC LIMIT 1"),
        {"camera_id": camera_id}
    ).fetchone()
    if not row:
        return {"data": None}
    return {"data": dict(row._mapping)}
