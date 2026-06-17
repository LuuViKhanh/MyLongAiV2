from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import require_admin

router = APIRouter()


@router.get("")
def list_users(current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT id, full_name, email, role, last_login, created_at FROM public.users ORDER BY created_at DESC")
    ).fetchall()
    return {"data": [dict(r._mapping) for r in rows]}


@router.get("/{id}")
def get_user(id: str, current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT id, full_name, email, role, last_login, created_at FROM public.users WHERE id = :id"),
        {"id": id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return dict(row._mapping)


@router.patch("/{id}/disable")
def disable_user(id: str, current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    result = db.execute(
        text("UPDATE public.users SET role = 'disabled' WHERE id = :id AND role != 'admin'"),
        {"id": id}
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User không tồn tại hoặc không thể khóa admin")
    return {"success": True, "user_id": id, "status": "disabled"}


@router.patch("/{id}/enable")
def enable_user(id: str, current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    result = db.execute(
        text("UPDATE public.users SET role = 'customer' WHERE id = :id"),
        {"id": id}
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return {"success": True, "user_id": id, "status": "enabled"}
