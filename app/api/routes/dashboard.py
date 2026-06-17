from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/overview")
def overview(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    total_users = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
    total_cameras = db.execute(text("SELECT COUNT(*) FROM cameras")).scalar()
    total_detections = db.execute(text("SELECT COUNT(*) FROM detections")).scalar()
    total_predictions = db.execute(text("SELECT COUNT(*) FROM drying_predictions")).scalar()
    return {
        "total_users": total_users,
        "total_cameras": total_cameras,
        "total_detections": total_detections,
        "total_predictions": total_predictions
    }
