from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import get_current_user
import uuid

router = APIRouter()


class CameraRequest(BaseModel):
    name: str
    location: str | None = None


@router.post("")
def create_camera(body: CameraRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    camera_id = str(uuid.uuid4())
    db.execute(
        text("INSERT INTO cameras (id, user_id, camera_name, location) VALUES (:id, :user_id, :camera_name, :location)"),
        {"id": camera_id, "user_id": current_user["sub"], "camera_name": body.name, "location": body.location}
    )
    db.commit()
    return {"success": True, "camera_id": camera_id}


@router.get("")
def list_cameras(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT id, camera_name, location, created_at FROM cameras WHERE user_id = :user_id"),
        {"user_id": current_user["sub"]}
    ).fetchall()
    return [{"id": str(r.id), "name": r.camera_name, "location": r.location, "created_at": str(r.created_at)} for r in rows]


@router.get("/{id}")
def get_camera(id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT id, camera_name, location, created_at FROM cameras WHERE id = :id AND user_id = :user_id"),
        {"id": id, "user_id": current_user["sub"]}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Camera không tồn tại")
    return {"id": str(row.id), "name": row.camera_name, "location": row.location, "created_at": str(row.created_at)}


@router.put("/{id}")
def update_camera(id: str, body: CameraRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    result = db.execute(
        text("UPDATE cameras SET camera_name = :camera_name, location = :location WHERE id = :id AND user_id = :user_id"),
        {"camera_name": body.name, "location": body.location, "id": id, "user_id": current_user["sub"]}
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Camera không tồn tại")
    return {"success": True}


@router.delete("/{id}")
def delete_camera(id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    result = db.execute(
        text("DELETE FROM cameras WHERE id = :id AND user_id = :user_id"),
        {"id": id, "user_id": current_user["sub"]}
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Camera không tồn tại")
    return {"success": True}
