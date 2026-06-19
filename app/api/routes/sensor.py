from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db

router = APIRouter()


@router.get("/latest/{camera_id}")
def get_latest(camera_id: str, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT * FROM sensor_readings WHERE camera_id = :camera_id ORDER BY recorded_at DESC LIMIT 1"),
        {"camera_id": camera_id}
    ).fetchone()
    if not row:
        return {"data": None}
    return {"data": dict(row._mapping)}


@router.get("/history/{camera_id}")
def get_history(camera_id: str, limit: int = 50, db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT * FROM sensor_readings WHERE camera_id = :camera_id ORDER BY recorded_at DESC LIMIT :limit"),
        {"camera_id": camera_id, "limit": limit}
    ).fetchall()
    return {"data": [dict(r._mapping) for r in rows]}
