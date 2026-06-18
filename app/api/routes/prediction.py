from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
import uuid

router = APIRouter()


class PredictionRequest(BaseModel):
    camera_id: str
    temperature: float
    humidity: float
    predicted_minutes: float


@router.post("")
def post_prediction(body: PredictionRequest, db: Session = Depends(get_db)):
    db.execute(
        text("INSERT INTO drying_predictions (id, camera_id, temperature, humidity, predicted_minutes) VALUES (:id, :camera_id, :temperature, :humidity, :predicted_minutes)"),
        {"id": str(uuid.uuid4()), "camera_id": body.camera_id, "temperature": body.temperature, "humidity": body.humidity, "predicted_minutes": body.predicted_minutes}
    )
    db.commit()
    return {"success": True}


@router.get("/latest/{camera_id}")
def get_latest(camera_id: str, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT * FROM drying_predictions WHERE camera_id = :camera_id ORDER BY created_at DESC LIMIT 1"),
        {"camera_id": camera_id}
    ).fetchone()
    if not row:
        return {"data": None}
    return {"data": dict(row._mapping)}
