from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import get_current_user
import uuid, hmac, hashlib, os, random, string

router = APIRouter()

SEPAY_SECRET = os.getenv("SEPAY_SECRET", "")
PREMIUM_AMOUNT = 10000
BIDV_ACCOUNT = "96247812005"
ACCOUNT_NAME = "LUU%20VI%20KHANH"


def generate_order_code() -> str:
    digits = ''.join(random.choices(string.digits, k=6))
    return f"MLAI{digits}"


def verify_sepay_signature(payload: bytes, signature: str) -> bool:
    if not SEPAY_SECRET or not signature:
        return True
    expected = hmac.new(SEPAY_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/create-order")
def create_order(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Kiểm tra đã Premium chưa
    user = db.execute(
        text("SELECT role FROM public.users WHERE id = :id"),
        {"id": current_user["sub"]}
    ).fetchone()
    if user and user.role == "premium":
        raise HTTPException(status_code=400, detail="Tài khoản đã là Premium")

    # Hủy các đơn pending cũ
    db.execute(
        text("UPDATE orders SET status = 'cancelled' WHERE user_id = :user_id AND status = 'pending'"),
        {"user_id": current_user["sub"]}
    )

    # Tạo đơn mới
    order_code = generate_order_code()
    db.execute(
        text("INSERT INTO orders (id, user_id, order_code, amount, status) VALUES (:id, :user_id, :order_code, :amount, 'pending')"),
        {"id": str(uuid.uuid4()), "user_id": current_user["sub"], "order_code": order_code, "amount": PREMIUM_AMOUNT}
    )
    db.commit()

    return {
        "order_code": order_code,
        "amount": PREMIUM_AMOUNT,
        "bank_account": BIDV_ACCOUNT,
        "bank_name": "BIDV",
        "account_name": "LUU VI KHANH",
        "content": order_code,
        "qr_url": f"https://img.vietqr.io/image/BIDV-{BIDV_ACCOUNT}-compact2.png?amount={PREMIUM_AMOUNT}&addInfo={order_code}&accountName={ACCOUNT_NAME}"
    }


@router.post("/webhook")
async def sepay_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("X-SePay-Signature", "")

    if not verify_sepay_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()

    # Lấy nội dung chuyển khoản
    content = data.get("content", "") or data.get("description", "")

    # Tìm mã MLAI trong nội dung
    order_code = None
    for word in content.upper().split():
        if word.startswith("MLAI"):
            order_code = word
            break

    if not order_code:
        return {"success": False, "message": "Không tìm thấy mã đơn hàng"}

    # Tìm đơn hàng
    order = db.execute(
        text("SELECT * FROM orders WHERE order_code = :code AND status = 'pending'"),
        {"code": order_code}
    ).fetchone()

    if not order:
        return {"success": False, "message": "Đơn hàng không tồn tại hoặc đã xử lý"}

    # Cập nhật đơn hàng
    db.execute(
        text("UPDATE orders SET status = 'paid', paid_at = NOW() WHERE order_code = :code"),
        {"code": order_code}
    )

    # Nâng cấp user lên Premium
    db.execute(
        text("UPDATE public.users SET role = 'premium' WHERE id = :user_id"),
        {"user_id": str(order.user_id)}
    )
    db.commit()

    return {"success": True, "message": "Nâng cấp Premium thành công"}


@router.get("/status")
def payment_status(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.execute(
        text("SELECT * FROM orders WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 1"),
        {"user_id": current_user["sub"]}
    ).fetchone()
    if not order:
        return {"status": "no_order"}
    return dict(order._mapping)
