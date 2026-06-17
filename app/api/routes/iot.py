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
    db.execute(
        text("INSERT INTO detections (id, camera_id, detected_count, confidence) VALUES (:id, :camera_id, :detected_count, :confidence)"),
        {"id": str(uuid.uuid4()), "camera_id": body.camera_id, "detected_count": body.detected_count, "confidence": body.confidence}
    )
    db.commit()
    return {"success": True}


@router.post("/dryness-result")
def ai_dryness(body: DrynessResultRequest, db: Session = Depends(get_db)):
    db.execute(
        text("INSERT INTO drying_predictions (id, camera_id, temperature, humidity, predicted_minutes) VALUES (:id, :camera_id, :temperature, :humidity, :predicted_minutes)"),
        {"id": str(uuid.uuid4()), "camera_id": body.camera_id, "temperature": body.temperature, "humidity": body.humidity, "predicted_minutes": body.predicted_minutes}
    )
    db.commit()
    return {"success": True}
