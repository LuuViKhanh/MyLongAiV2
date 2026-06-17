from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import require_admin

router = APIRouter()


@router.get("")
def list_subscriptions(current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT * FROM subscriptions ORDER BY transaction_time DESC")
    ).fetchall()
    return {"data": [dict(r._mapping) for r in rows]}


@router.get("/statistics")
def revenue_statistics(current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    today = db.execute(text("""
        SELECT COALESCE(SUM(amount), 0) FROM subscriptions
        WHERE payment_status = 'paid' AND DATE(transaction_time) = CURRENT_DATE
    """)).scalar()

    month = db.execute(text("""
        SELECT COALESCE(SUM(amount), 0) FROM subscriptions
        WHERE payment_status = 'paid'
        AND DATE_TRUNC('month', transaction_time) = DATE_TRUNC('month', CURRENT_DATE)
    """)).scalar()

    year = db.execute(text("""
        SELECT COALESCE(SUM(amount), 0) FROM subscriptions
        WHERE payment_status = 'paid'
        AND DATE_TRUNC('year', transaction_time) = DATE_TRUNC('year', CURRENT_DATE)
    """)).scalar()

    return {
        "today": float(today),
        "month": float(month),
        "year": float(year)
    }
