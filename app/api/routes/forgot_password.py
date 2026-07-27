from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import hash_password
import secrets, os, resend
from datetime import datetime, timedelta, timezone

router = APIRouter()

resend.api_key = os.getenv("RESEND_API_KEY", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://batchguard-web.vercel.app")


def send_email(to: str, subject: str, html: str):
    try:
        resend.Emails.send({
            "from": "MyLongAI <onboarding@resend.dev>",
            "to": to,
            "subject": subject,
            "html": html
        })
    except Exception as e:
        print(f"[Email Error] {e}")


class ForgotRequest(BaseModel):
    email: EmailStr


class ResetRequest(BaseModel):
    token: str
    new_password: str


@router.post("/forgot")
def forgot_password(body: ForgotRequest, db: Session = Depends(get_db)):
    user = db.execute(
        text("SELECT id, email FROM public.users WHERE email = :email"),
        {"email": body.email}
    ).fetchone()

    # Luôn trả về success để tránh lộ email tồn tại hay không
    if not user:
        return {"success": True, "message": "Nếu email tồn tại, bạn sẽ nhận được hướng dẫn."}

    # Tạo token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

    # Xóa token cũ
    db.execute(text("DELETE FROM password_resets WHERE email = :email"), {"email": body.email})

    # Lưu token mới
    db.execute(
        text("INSERT INTO password_resets (email, token, expires_at) VALUES (:email, :token, :expires_at)"),
        {"email": body.email, "token": token, "expires_at": expires_at}
    )
    db.commit()

    # Gửi email
    reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">MyLongAI — Đặt lại mật khẩu</h2>
        <p>Bạn đã yêu cầu đặt lại mật khẩu. Click vào nút bên dưới:</p>
        <a href="{reset_url}" style="background: #2563eb; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; display: inline-block; margin: 16px 0;">
            Đặt lại mật khẩu
        </a>
        <p style="color: #666;">Link có hiệu lực trong <strong>30 phút</strong>.</p>
        <p style="color: #666;">Nếu bạn không yêu cầu, hãy bỏ qua email này.</p>
    </div>
    """
    send_email(body.email, "MyLongAI — Đặt lại mật khẩu", html)

    return {"success": True, "message": "Nếu email tồn tại, bạn sẽ nhận được hướng dẫn."}


@router.post("/reset")
def reset_password(body: ResetRequest, db: Session = Depends(get_db)):
    record = db.execute(
        text("SELECT * FROM password_resets WHERE token = :token AND used = FALSE"),
        {"token": body.token}
    ).fetchone()

    if not record:
        raise HTTPException(status_code=400, detail="Token không hợp lệ hoặc đã được sử dụng")

    if datetime.now(timezone.utc) > record.expires_at:
        raise HTTPException(status_code=400, detail="Token đã hết hạn. Vui lòng yêu cầu lại.")

    # Đổi mật khẩu
    db.execute(
        text("UPDATE public.users SET password_hash = :hash WHERE email = :email"),
        {"hash": hash_password(body.new_password), "email": record.email}
    )

    # Đánh dấu token đã dùng
    db.execute(
        text("UPDATE password_resets SET used = TRUE WHERE token = :token"),
        {"token": body.token}
    )
    db.commit()

    return {"success": True, "message": "Đổi mật khẩu thành công"}
