# Hướng Dẫn Tích Hợp Quên Mật Khẩu — Frontend

**Base URL:** `https://mylongaiv2.onrender.com`

---

## Luồng hoạt động

```
1. [User nhập email]  ──► POST /auth/forgot  ──► [Backend gửi email reset]
2. [User nhận email]  ──► Click link          ──► [Chuyển đến trang /reset-password?token=xxx]
3. [User nhập pass mới] ──► POST /auth/reset  ──► [Đổi mật khẩu thành công]
```

---

## Bước 1 — Trang Quên Mật Khẩu

Tạo form cho user nhập email, gọi API:

**`POST /auth/forgot`**

```js
const response = await fetch("https://mylongaiv2.onrender.com/auth/forgot", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email: "user@example.com" })
});

const data = await response.json();
// { "success": true, "message": "Nếu email tồn tại, bạn sẽ nhận được hướng dẫn." }
```

> Backend luôn trả `success: true` dù email có tồn tại hay không (bảo mật).  
> User sẽ nhận email từ `onboarding@resend.dev` với link reset.

---

## Bước 2 — Trang Reset Mật Khẩu (`/reset-password`)

Frontend **bắt buộc phải có route `/reset-password`**. Link trong email sẽ trỏ đến:

```
https://batchguard-web.vercel.app/reset-password?token=TOKEN_Ở_ĐÂY
```

Khi user vào trang này, đọc token từ URL:

```js
// React
const params = new URLSearchParams(window.location.search);
const token = params.get("token");

// Next.js (App Router)
const { searchParams } = new URL(request.url);
const token = searchParams.get("token");
```

Hiển thị form nhập mật khẩu mới, gọi API:

**`POST /auth/reset`**

```js
const response = await fetch("https://mylongaiv2.onrender.com/auth/reset", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    token: token,         // lấy từ URL
    new_password: "matkhaumoi123"
  })
});

const data = await response.json();
// { "success": true, "message": "Đổi mật khẩu thành công" }
```

Sau khi thành công → redirect về trang `/login`.

---

## Xử lý lỗi

| HTTP Status | Lỗi | Hiển thị cho user |
|-------------|-----|-------------------|
| 400 | `"Token không hợp lệ hoặc đã được sử dụng"` | "Link đặt lại mật khẩu không hợp lệ." |
| 400 | `"Token đã hết hạn. Vui lòng yêu cầu lại."` | "Link đã hết hạn. Vui lòng thử lại." |

```js
if (!response.ok) {
  const err = await response.json();
  // err.detail chứa thông báo lỗi
  alert(err.detail);
}
```

---

## Lưu ý

- Link reset có hiệu lực **30 phút** kể từ lúc gửi
- Mỗi lần gọi `POST /auth/forgot`, token cũ sẽ bị hủy và tạo token mới
- Token chỉ dùng được **1 lần** — sau khi đổi mật khẩu thành công, token bị đánh dấu đã dùng
