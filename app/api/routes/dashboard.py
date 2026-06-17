from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import require_admin

router = APIRouter()


@router.get("/overview")
def overview(current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    total_users = db.execute(text("SELECT COUNT(*) FROM public.users")).scalar()
    total_cameras = db.execute(text("SELECT COUNT(*) FROM cameras")).scalar()
    total_detections = db.execute(text("SELECT COUNT(*) FROM detections")).scalar()
    total_predictions = db.execute(text("SELECT COUNT(*) FROM drying_predictions")).scalar()
    return {
        "total_users": total_users,
        "total_cameras": total_cameras,
        "total_detections": total_detections,
        "total_predictions": total_predictions
    }


@router.get("/admin")
def admin_dashboard(current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    customer_count = db.execute(text("SELECT COUNT(*) FROM public.users WHERE role = 'customer'")).scalar()
    camera_count = db.execute(text("SELECT COUNT(*) FROM cameras")).scalar()
    online_camera_count = db.execute(text("SELECT COUNT(*) FROM cameras WHERE status = 'online'")).scalar()
    total_revenue = db.execute(text("SELECT COALESCE(SUM(amount), 0) FROM subscriptions WHERE payment_status = 'paid'")).scalar()
    return {
        "customer_count": customer_count,
        "camera_count": camera_count,
        "online_camera_count": online_camera_count,
        "total_revenue": float(total_revenue)
    }


@router.get("/admin/confidence-chart")
def confidence_chart(current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT DATE(detected_at) as date, ROUND(AVG(confidence)::numeric, 2) as avg_confidence, SUM(detected_count) as total_detected
        FROM detections
        GROUP BY DATE(detected_at)
        ORDER BY date DESC
        LIMIT 30
    """)).fetchall()
    return {"data": [dict(r._mapping) for r in rows]}


@router.get("/admin/dryness-chart")
def dryness_chart(current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT DATE(created_at) as date, ROUND(AVG(predicted_minutes)::numeric, 2) as avg_minutes, ROUND(AVG(humidity)::numeric, 2) as avg_humidity, ROUND(AVG(temperature)::numeric, 2) as avg_temperature
        FROM drying_predictions
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        LIMIT 30
    """)).fetchall()
    return {"data": [dict(r._mapping) for r in rows]}
