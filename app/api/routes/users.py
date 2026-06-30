from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import require_admin


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

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


@router.put("/{id}")
def update_user(id: str, body: UpdateUserRequest, current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="Không có dữ liệu cập nhật")
    set_clause = ", ".join(f"{k} = :{k}" for k in fields)
    fields["id"] = id
    result = db.execute(text(f"UPDATE public.users SET {set_clause} WHERE id = :id"), fields)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return {"success": True, "user_id": id}


@router.delete("/{id}")
def delete_user(id: str, current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if id == current_user["sub"]:
        raise HTTPException(status_code=400, detail="Không thể tự xóa chính mình")
    # Xóa các bảng liên quan trước (cascade thủ công)
    camera_ids = [r[0] for r in db.execute(text("SELECT id FROM public.cameras WHERE user_id = :id"), {"id": id}).fetchall()]
    for cam_id in camera_ids:
        db.execute(text("DELETE FROM public.detections WHERE camera_id = :cam_id"), {"cam_id": cam_id})
        db.execute(text("DELETE FROM public.drying_predictions WHERE camera_id = :cam_id"), {"cam_id": cam_id})
        db.execute(text("DELETE FROM public.sensor_readings WHERE camera_id = :cam_id"), {"cam_id": cam_id})
    db.execute(text("DELETE FROM public.cameras WHERE user_id = :id"), {"id": id})
    db.execute(text("DELETE FROM public.subscriptions WHERE user_id = :id"), {"id": id})
    db.execute(text("DELETE FROM orders WHERE user_id = :id"), {"id": id})
    db.execute(text("DELETE FROM notifications WHERE user_id = :id"), {"id": id})
    db.execute(text("DELETE FROM password_resets WHERE email = (SELECT email FROM public.users WHERE id = :id)"), {"id": id})
    result = db.execute(
        text("DELETE FROM public.users WHERE id = :id AND role != 'admin'"),
        {"id": id}
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User không tồn tại hoặc không thể xóa admin")
    return {"success": True, "user_id": id}


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
