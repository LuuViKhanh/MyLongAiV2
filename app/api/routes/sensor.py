from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
import uuid

router = APIRouter()


class SensorRequest(BaseModel):
    camera_id: str
    temperature: float
    humidity: float


@router.post("")
def post_sensor(body: SensorRequest, db: Session = Depends(get_db)):
    db.execute(
        text("INSERT INTO sensor_readings (id, camera_id, temperature, humidity) VALUES (:id, :camera_id, :temperature, :humidity)"),
        {"id": str(uuid.uuid4()), "camera_id": body.camera_id, "temperature": body.temperature, "humidity": body.humidity}
    )
    db.commit()
    return {"success": True}


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
