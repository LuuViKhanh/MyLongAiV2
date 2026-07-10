# MyLongAI Backend v2 — Tài liệu API

**Production:** `https://mylongaiv2.onrender.com`  
**Swagger UI:** `https://mylongaiv2.onrender.com/docs`

---

## Xác thực (Authentication)

Hầu hết API yêu cầu JWT Bearer token. Lấy token từ `POST /auth/login`, sau đó gửi kèm header:

```
Authorization: Bearer <access_token>
```

**Roles:** `customer` (free) | `premium` | `admin`

---

## Giới hạn theo gói

| Tính năng | Free | Premium |
|-----------|------|---------|
| Số camera | 1 | Không giới hạn |
| Lịch sử sensor | 2 ngày | Toàn bộ |
| Detection/ngày | 10 lần | Không giới hạn |
| Dự đoán thời gian phơi | ❌ | ✅ |
| Lời khuyên thời tiết | ❌ (🔒) | ✅ |

---

## Auth — `/auth`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| POST | `/auth/register` | ❌ | Đăng ký tài khoản |
| POST | `/auth/login` | ❌ | Đăng nhập, nhận JWT |
| GET | `/auth/profile` | ✅ | Xem thông tin tài khoản |


### POST `/auth/register`
```json
// Request
{ "name": "Nguyễn Văn A", "email": "user@example.com", "password": "123456" }

// Response
{ "success": true, "user_id": "uuid" }
```

### POST `/auth/login`
```json
// Request
{ "email": "user@example.com", "password": "123456" }

// Response
{ "access_token": "...", "token_type": "bearer", "user_id": "uuid", "name": "Nguyễn Văn A", "role": "customer" }
```

### GET `/auth/profile`
```json
// Response
{ "id": "uuid", "name": "Nguyễn Văn A", "email": "user@example.com", "role": "premium", "premium_expired_at": "2025-02-01T00:00:00" }
```

---

## Camera — `/camera`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| POST | `/camera` | ✅ | Thêm camera mới |
| GET | `/camera` | ✅ | Danh sách camera |
| GET | `/camera/{id}` | ✅ | Chi tiết camera |
| PUT | `/camera/{id}` | ✅ | Cập nhật camera |
| DELETE | `/camera/{id}` | ✅ | Xóa camera (cascade) |

> Free: tối đa 1 camera. Admin xem được tất cả camera của mọi user.

### POST `/camera`
```json
// Request
{ "name": "Camera sân phơi 1", "location": "Khu A" }

// Response
{ "success": true, "camera_id": "uuid" }
```

### GET `/camera`
```json
// Response
[{ "id": "uuid", "name": "Camera sân phơi 1", "location": "Khu A", "user_id": "uuid", "created_at": "..." }]
```

---

## Sensor — `/sensor`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/sensor/latest/{camera_id}` | ❌ | Dữ liệu cảm biến mới nhất |
| GET | `/sensor/history/{camera_id}` | ✅ | Lịch sử cảm biến |

### GET `/sensor/history/{camera_id}?limit=50`
```json
// Response
{
  "data": [{ "id": "uuid", "camera_id": "uuid", "temperature": 33.5, "humidity": 72.0, "recorded_at": "..." }],
  "plan": "free"
}
```
> Free: chỉ trả về 2 ngày gần nhất. Premium: toàn bộ lịch sử.

---

## Detection — `/detection`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/detection/latest/{camera_id}` | ❌ | Kết quả nhận diện mới nhất |

### GET `/detection/latest/{camera_id}`
```json
// Response
{ "data": { "id": "uuid", "camera_id": "uuid", "detected_count": 12, "confidence": 0.94, "detected_at": "..." } }
```

---

## Prediction — `/prediction`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/prediction/latest/{camera_id}` | ✅ Premium | Dự đoán thời gian phơi mới nhất |

### GET `/prediction/latest/{camera_id}`
```json
// Response
{ "data": { "id": "uuid", "camera_id": "uuid", "temperature": 34.0, "humidity": 65.0, "predicted_minutes": 45.5, "created_at": "..." } }
```

---

## IoT & AI Internal — `/iot`

Dùng cho ESP32 và AI model gửi dữ liệu lên server. Không cần auth.

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| POST | `/iot/sensor-data` | ❌ | ESP32 gửi nhiệt độ, độ ẩm |
| POST | `/iot/detection-result` | ❌ | AI gửi kết quả nhận diện |
| POST | `/iot/dryness-result` | ❌ | AI gửi dự đoán thời gian phơi |

### POST `/iot/sensor-data`
```json
// Request
{ "camera_id": "uuid", "temperature": 33.5, "humidity": 72.0 }

// Response
{ "success": true }
```

### POST `/iot/detection-result`
```json
// Request
{ "camera_id": "uuid", "detected_count": 12, "confidence": 0.94 }

// Response (Free đã đạt giới hạn)
{ "success": false, "message": "Đã đạt giới hạn 10 lần detect/ngày. Nâng cấp Premium để dùng không giới hạn." }
```

### POST `/iot/dryness-result`
```json
// Request
{ "camera_id": "uuid", "temperature": 34.0, "humidity": 65.0, "predicted_minutes": 45.5 }

// Response (camera thuộc Free user)
{ "success": false, "message": "Camera này thuộc tài khoản Free, không hỗ trợ dự đoán" }
```

---

## Weather AI — `/weather`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/weather/analyze` | ❌ (optional) | Phân tích thời tiết + dự đoán mưa |


### GET `/weather/analyze?lat=10.226&lon=106.421&save=true`
```json
// Response (Premium)
{
  "timestamp": "2025-01-01T10:00:00",
  "location": { "lat": 10.226, "lon": 106.421 },
  "api_weather": {
    "temperature_c": 32.5, "humidity_percent": 78,
    "pressure_hpa": 1010.2, "wind_speed_ms": 3.2,
    "precipitation_mm": 0.0, "weather_code": 2
  },
  "sensor_data": {
    "temperature_c": 33.1, "humidity_percent": 82.5,
    "source": "real_sensor"
  },
  "prediction": {
    "rain_score": 55.0, "rain_level": "medium",
    "rain_label": "Có thể có mưa",
    "max_precip_probability_12h": 60,
    "currently_raining": false
  },
  "advice": ["🌦️ Có thể có mưa — không nên phơi bánh tráng lúc này."],
  "record_id": 42
}

// Response (Free / Guest)
{ ..., "advice": ["🔒 Nâng cấp Premium để nhận khuyến nghị phơi bánh tráng."] }
```

**Logic tính điểm mưa (0–100):**

| Yếu tố | Điểm |
|--------|------|
| Xác suất mưa 12h (Open-Meteo) | 50 |
| Độ ẩm IoT > 60% | 30 |
| Đang có mưa | 10 |
| Mã thời tiết WMO (mưa/dông) | 5 |
| Độ ẩm khí tượng > 85% | 5 |
| Gió > 5 m/s | 5 |

| Điểm | Mức | Nhãn |
|------|-----|------|
| ≥ 70 | `high` | Khả năng mưa cao |
| 40–69 | `medium` | Có thể có mưa |
| < 40 | `low` | Ít khả năng mưa |

---

## Notification — `/notification`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| POST | `/notification` | ❌ | Tạo thông báo mới |
| GET | `/notification/me` | ✅ | Xem thông báo của mình |

### POST `/notification`
```json
// Request
{ "user_id": "uuid", "camera_id": "uuid", "weather_status": "rain_high", "advice": "Thu bánh tráng ngay!" }

// Response
{ "success": true }
```

---

## Payment — `/payment`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| POST | `/payment/create-order` | ✅ | Tạo đơn hàng nâng cấp Premium |
| POST | `/payment/webhook` | ❌ | SePay webhook xác nhận thanh toán |
| GET | `/payment/status` | ✅ | Kiểm tra trạng thái đơn hàng |

### POST `/payment/create-order`
```json
// Response
{
  "order_code": "MLAI123456",
  "amount": 10000,
  "bank_account": "96247812005",
  "bank_name": "BIDV",
  "account_name": "LUU VI KHANH",
  "content": "MLAI123456",
  "qr_url": "https://img.vietqr.io/image/BIDV-96247812005-compact2.png?amount=10000&addInfo=MLAI123456&accountName=LUU%20VI%20KHANH"
}
```
> Chuyển khoản đúng nội dung `MLAI123456` để hệ thống tự xác nhận.  
> Premium cộng dồn 30 ngày nếu đang còn hạn.

### POST `/payment/webhook`
> Gọi bởi SePay khi có giao dịch. Tự động tìm mã `MLAI\d+` trong nội dung chuyển khoản.

### GET `/payment/status`
```json
// Response
{ "id": "uuid", "user_id": "uuid", "order_code": "MLAI123456", "amount": 10000, "status": "paid", "paid_at": "..." }
```

---

## Voice Alert — `/voice`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/voice/alert` | ❌ | Phát cảnh báo mưa bằng giọng nói |
| GET | `/voice/custom` | ❌ | Đọc văn bản tùy chỉnh |

### GET `/voice/alert?level=high`
> `level`: `low` | `medium` | `high`  
> Trả về file MP3 (audio/mpeg) stream.

| Level | Nội dung |
|-------|----------|
| `high` | "Cảnh báo! Khả năng mưa cao. Hãy thu bánh tráng vào ngay và tạm dừng sản xuất." |
| `medium` | "Chú ý! Có thể có mưa. Không nên phơi bánh tráng lúc này." |
| `low` | "Thời tiết ổn định. Thuận lợi để phơi bánh tráng." |

### GET `/voice/custom?text=Xin chào`
> Trả về file MP3 đọc nội dung `text` bằng tiếng Việt.

---

## Dashboard — `/dashboard` *(Admin only)*

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/dashboard/overview` | ✅ Admin | Tổng quan hệ thống |
| GET | `/dashboard/admin` | ✅ Admin | Thống kê admin |
| GET | `/dashboard/admin/confidence-chart` | ✅ Admin | Biểu đồ confidence 30 ngày |
| GET | `/dashboard/admin/dryness-chart` | ✅ Admin | Biểu đồ dryness 30 ngày |

### GET `/dashboard/overview`
```json
{ "total_users": 150, "total_cameras": 45, "total_detections": 3200, "total_predictions": 800 }
```

### GET `/dashboard/admin`
```json
{ "customer_count": 140, "camera_count": 45, "online_camera_count": 12, "total_revenue": 500000.0 }
```

---

## User Management — `/users` *(Admin only)*

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/users` | ✅ Admin | Danh sách tất cả user |
| GET | `/users/{id}` | ✅ Admin | Chi tiết user |
| PUT | `/users/{id}` | ✅ Admin | Cập nhật user |
| DELETE | `/users/{id}` | ✅ Admin | Xóa user (cascade) |
| PATCH | `/users/{id}/disable` | ✅ Admin | Khóa tài khoản |
| PATCH | `/users/{id}/enable` | ✅ Admin | Mở khóa tài khoản |

> DELETE cascade: xóa cameras, detections, sensor_readings, drying_predictions, subscriptions, orders, notifications, password_resets.  
> Không thể xóa hoặc khóa tài khoản `admin`.

---

## Revenue — `/subscriptions` *(Admin only)*

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/subscriptions` | ✅ Admin | Danh sách giao dịch |
| GET | `/subscriptions/statistics` | ✅ Admin | Doanh thu theo ngày/tháng/năm |

### GET `/subscriptions/statistics`
```json
{ "today": 10000.0, "month": 150000.0, "year": 800000.0 }
```

---

## Health Check

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/` | ❌ | Root health check |
| GET | `/health/` | ❌ | Health check |

```json
{ "status": "ok" }
```

---

## Error Responses

| Status | Mô tả |
|--------|-------|
| 400 | Dữ liệu không hợp lệ |
| 401 | Chưa đăng nhập hoặc token hết hạn |
| 403 | Không đủ quyền (cần Premium hoặc Admin) |
| 404 | Không tìm thấy resource |

```json
{ "detail": "Mô tả lỗi" }
```

---

## Tech Stack

- **FastAPI** + **SQLAlchemy** — Web framework & ORM
- **Supabase PostgreSQL** — Database (SSL)
- **Open-Meteo API** — Dữ liệu khí tượng (miễn phí)
- **SePay + VietQR BIDV** — Thanh toán (VA `96247812005`)
- **Resend API** — Gửi email
- **gTTS** — Text-to-speech tiếng Việt
- **Render** — Hosting production
