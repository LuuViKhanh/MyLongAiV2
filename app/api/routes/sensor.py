from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import get_current_user, require_premium
from datetime import datetime, timedelta

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
def get_history(camera_id: str, limit: int = 50, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    is_premium = current_user.get("role") in ("premium", "admin")
    if is_premium:
        rows = db.execute(
            text("SELECT * FROM sensor_readings WHERE camera_id = :camera_id ORDER BY recorded_at DESC LIMIT :limit"),
            {"camera_id": camera_id, "limit": limit}
        ).fetchall()
    else:
        since = datetime.utcnow() - timedelta(days=2)
        rows = db.execute(
            text("SELECT * FROM sensor_readings WHERE camera_id = :camera_id AND recorded_at >= :since ORDER BY recorded_at DESC LIMIT :limit"),
            {"camera_id": camera_id, "since": since, "limit": limit}
        ).fetchall()
    return {"data": [dict(r._mapping) for r in rows], "plan": "premium" if is_premium else "free"}
