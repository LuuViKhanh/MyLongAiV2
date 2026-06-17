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
        text("INSERT INTO public.users (id, full_name, email, password_hash) VALUES (:id, :full_name, :email, :password_hash)"),
        {"id": user_id, "full_name": body.name, "email": body.email, "password_hash": hash_password(body.password)}
    )
    db.commit()
    return {"success": True, "user_id": user_id}


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(
        text("SELECT id, email, password_hash, full_name FROM public.users WHERE email = :email"),
        {"email": body.email}
    ).fetchone()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    token = create_token(str(user.id), user.email)
    return {"access_token": token, "token_type": "bearer", "user_id": str(user.id), "name": user.full_name}


@router.get("/profile")
def profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.execute(
        text("SELECT id, full_name, email FROM public.users WHERE id = :id"),
        {"id": current_user["sub"]}
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")
    return {"id": str(user.id), "name": user.full_name, "email": user.email}
