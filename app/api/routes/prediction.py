from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import require_premium

router = APIRouter()


@router.get("/latest/{camera_id}")
def get_latest(camera_id: str, current_user: dict = Depends(require_premium), db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT * FROM drying_predictions WHERE camera_id = :camera_id ORDER BY created_at DESC LIMIT 1"),
        {"camera_id": camera_id}
    ).fetchone()
    if not row:
        return {"data": None}
    return {"data": dict(row._mapping)}
