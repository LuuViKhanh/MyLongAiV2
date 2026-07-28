from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import hash_password, verify_password, create_token, get_current_user
import uuid

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.execute(
        text("SELECT id FROM public.users WHERE email = :email"),
        {"email": body.email}
    ).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Email đã được đăng ký")

    user_id = str(uuid.uuid4())
    db.execute(
        text("INSERT INTO public.users (id, full_name, email, password_hash, role) VALUES (:id, :full_name, :email, :password_hash, 'customer')"),
        {"id": user_id, "full_name": body.name, "email": body.email, "password_hash": hash_password(body.password)}
    )
    db.commit()
    return {"success": True, "user_id": user_id}


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(
        text("SELECT id, email, password_hash, full_name, role, premium_expired_at FROM public.users WHERE email = :email"),
        {"email": body.email}
    ).fetchone()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    # Kiểm tra hết hạn Premium
    role = user.role
    if role == "premium" and user.premium_expired_at:
        from datetime import datetime, timezone
        if datetime.now(timezone.utc) > user.premium_expired_at:
            db.execute(text("UPDATE public.users SET role = 'customer' WHERE id = :id"), {"id": str(user.id)})
            db.commit()
            role = "customer"

    token = create_token(str(user.id), user.email, role)
    return {"access_token": token, "token_type": "bearer", "user_id": str(user.id), "name": user.full_name, "role": role}


@router.get("/profile")
def profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.execute(
        text("SELECT id, full_name, email, role, premium_expired_at FROM public.users WHERE id = :id"),
        {"id": current_user["sub"]}
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")

    # Kiểm tra hết hạn Premium
    role = user.role
    if role == "premium" and user.premium_expired_at:
        from datetime import datetime, timezone
        if datetime.now(timezone.utc) > user.premium_expired_at:
            db.execute(text("UPDATE public.users SET role = 'customer' WHERE id = :id"), {"id": str(user.id)})
            db.commit()
            role = "customer"

    return {"id": str(user.id), "name": user.full_name, "email": user.email, "role": role, "premium_expired_at": str(user.premium_expired_at) if user.premium_expired_at else None}
