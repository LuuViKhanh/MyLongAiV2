from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
import uuid

router = APIRouter()


class SensorDataRequest(BaseModel):
    camera_id: str
    temperature: float
    humidity: float


class DetectionResultRequest(BaseModel):
    camera_id: str
    detected_count: int
    confidence: float


class DrynessResultRequest(BaseModel):
    camera_id: str
    temperature: float
    humidity: float
    predicted_minutes: float


@router.post("/sensor-data")
def esp32_sensor(body: SensorDataRequest, db: Session = Depends(get_db)):
    db.execute(
        text("INSERT INTO sensor_readings (id, camera_id, temperature, humidity) VALUES (:id, :camera_id, :temperature, :humidity)"),
        {"id": str(uuid.uuid4()), "camera_id": body.camera_id, "temperature": body.temperature, "humidity": body.humidity}
    )
    db.commit()
    return {"success": True}


@router.post("/detection-result")
def ai_detection(body: DetectionResultRequest, db: Session = Depends(get_db)):
    # Kiểm tra giới hạn 10 lần detect/ngày cho Free
    camera = db.execute(
        text("SELECT user_id FROM cameras WHERE id = :camera_id"),
        {"camera_id": body.camera_id}
    ).fetchone()
    if camera:
        user = db.execute(
            text("SELECT role FROM public.users WHERE id = :id"),
            {"id": str(camera.user_id)}
        ).fetchone()
        if user and user.role not in ("premium", "admin"):
            count_today = db.execute(
                text("SELECT COUNT(*) FROM detections WHERE camera_id = :camera_id AND DATE(detected_at) = CURRENT_DATE"),
                {"camera_id": body.camera_id}
            ).scalar()
            if count_today >= 10:
                return {"success": False, "message": "Đã đạt giới hạn 10 lần detect/ngày. Nâng cấp Premium để dùng không giới hạn."}
    db.execute(
        text("INSERT INTO detections (id, camera_id, detected_count, confidence) VALUES (:id, :camera_id, :detected_count, :confidence)"),
        {"id": str(uuid.uuid4()), "camera_id": body.camera_id, "detected_count": body.detected_count, "confidence": body.confidence}
    )
    db.commit()
    return {"success": True}


@router.post("/dryness-result")
def ai_dryness(body: DrynessResultRequest, db: Session = Depends(get_db)):
    # Kiểm tra camera thuộc user premium không
    camera = db.execute(
        text("SELECT user_id FROM cameras WHERE id = :camera_id"),
        {"camera_id": body.camera_id}
    ).fetchone()
    if camera:
        user = db.execute(
            text("SELECT role FROM public.users WHERE id = :id"),
            {"id": str(camera.user_id)}
        ).fetchone()
        if user and user.role not in ("premium", "admin"):
            return {"success": False, "message": "Camera này thuộc tài khoản Free, không hỗ trợ dự đoán"}
    db.execute(
        text("INSERT INTO drying_predictions (id, camera_id, temperature, humidity, predicted_minutes) VALUES (:id, :camera_id, :temperature, :humidity, :predicted_minutes)"),
        {"id": str(uuid.uuid4()), "camera_id": body.camera_id, "temperature": body.temperature, "humidity": body.humidity, "predicted_minutes": body.predicted_minutes}
    )
    db.commit()
    return {"success": True}
