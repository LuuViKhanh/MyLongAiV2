# Tài Liệu Tích Hợp — MyLongAI Backend v2

Tài liệu này trả lời trực tiếp các yêu cầu từ **Camera Relay v3** để tích hợp với **MyLongAI Backend (mylongaiv2)**.

**Production:** `https://mylongaiv2.onrender.com`

---

## 1. Biến Môi Trường JWT

| Yêu cầu từ v3 | Giá trị thực tế bên Main BE | Ghi chú |
|:---|:---|:---|
| `JWT_SECRET` | Tên biến là **`SECRET_KEY`** | Cần dùng đúng tên `SECRET_KEY` khi config v3 |
| `JWT_ALGORITHM` | `HS256` | Khớp ✅ |

> ⚠️ Lưu ý: biến môi trường bên Main BE tên là `SECRET_KEY`, không phải `JWT_SECRET`. Camera Relay v3 cần đọc đúng tên này, hoặc hai bên thống nhất đổi tên chung.

---

## 2. JWT Payload

Khi `POST /auth/login` thành công, token trả về có payload:

```json
{
  "sub": "uuid-cua-user",
  "email": "user@example.com",
  "role": "customer",
  "exp": 1720000000
}
```

| Trường | Mô tả |
|:---|:---|
| `sub` | UUID của user — dùng để đếm phiên kết nối đồng thời |
| `role` | `customer` = Free (tối đa 1 camera), `premium` / `admin` = không giới hạn |
| `exp` | Hết hạn sau **7 ngày** kể từ lúc login |

Token ký bằng `HS256` + `SECRET_KEY`. Camera Relay v3 verify trực tiếp mà không cần gọi về Main BE.

---

## 3. Bảng `cameras`

```
cameras:
  id          UUID  (Primary Key)
  user_id     UUID  (Foreign Key → users.id)
  camera_name TEXT
  location    TEXT
  created_at  TIMESTAMP
```

---

## 4. API Camera

### GET `/camera`
Trả danh sách camera thuộc user hiện tại (dựa theo JWT token).

**Header:** `Authorization: Bearer <access_token>`

```json
// Response
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Camera sân phơi 1",
    "location": "Khu A",
    "user_id": "uuid-cua-user",
    "created_at": "2025-01-01T08:00:00"
  }
]
```

### GET `/camera/{id}`
Trả chi tiết một camera theo UUID.

**Header:** `Authorization: Bearer <access_token>`

```json
// Response
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Camera sân phơi 1",
  "location": "Khu A",
  "user_id": "uuid-cua-user",
  "created_at": "2025-01-01T08:00:00"
}
```

---

## 5. Quy Trình Phối Hợp

```
1. [Main BE]        ── Phát JWT (sub, role, exp) ──────────► [Frontend]
2. [Main BE]        ── Cung cấp camera UUID ──────────────► [Frontend]
3. [Laptop Xưởng]  ── Đẩy stream với camera UUID ────────► [Camera Relay v3]
4. [Frontend]       ── Gửi JWT + camera UUID ────────────► [Camera Relay v3]
                                                              └─ Verify bằng SECRET_KEY
                                                              └─ Kiểm tra role → giới hạn kết nối
                                                              └─ Cho xem video
```

---

## 6. Checklist Tích Hợp

- [x] JWT payload có `sub`, `role`, `exp`
- [x] Thuật toán `HS256`
- [x] Token hợp lệ 7 ngày
- [x] Bảng `cameras` có `id` dạng UUID
- [x] `GET /camera` trả danh sách kèm `id`
- [x] `GET /camera/{id}` trả chi tiết
- [ ] Hai bên thống nhất tên biến: `SECRET_KEY` hay `JWT_SECRET`
