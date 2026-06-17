from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import get_current_user
import uuid

router = APIRouter()


class NotificationRequest(BaseModel):
    user_id: str
    camera_id: str
    weather_status: str
    advice: str


@router.post("")
def post_notification(body: NotificationRequest, db: Session = Depends(get_db)):
    db.execute(
        text("INSERT INTO notifications (id, user_id, camera_id, weather_status, advice, is_sent) VALUES (:id, :user_id, :camera_id, :weather_status, :advice, false)"),
        {"id": str(uuid.uuid4()), "user_id": body.user_id, "camera_id": body.camera_id, "weather_status": body.weather_status, "advice": body.advice}
    )
    db.commit()
    return {"success": True}


@router.get("/{user_id}")
def get_notifications(user_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    rows = db.execute(
        text("SELECT * FROM notifications WHERE user_id = :user_id ORDER BY created_at DESC"),
        {"user_id": user_id}
    ).fetchall()
    return {"data": [dict(r._mapping) for r in rows]}
