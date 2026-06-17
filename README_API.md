# API Documentation — MyLongAI Backend

Base URL: `https://mylongaiv2.onrender.com`

Swagger UI (thử trực tiếp): `https://mylongaiv2.onrender.com/docs`

---

## Xác thực (Authentication)

Các API có ký hiệu 🔒 yêu cầu **Bearer Token** trong header:

```
Authorization: Bearer <access_token>
```

Token lấy từ `/auth/login`.

---

## 1. Auth

### POST `/auth/register` — Đăng ký

**Body:**
```json
{
  "name": "Nguyễn Văn A",
  "email": "user@example.com",
  "password": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "uuid"
}
```

**Lỗi:**
| Code | Mô tả |
|------|-------|
| 400 | Email đã được đăng ký |

---

### POST `/auth/login` — Đăng nhập

**Body:**
```json
{
  "email": "user@example.com",
  "password": "123456"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user_id": "uuid",
  "name": "Nguyễn Văn A"
}
```

> Lưu `access_token` vào localStorage để dùng cho các API khác.

**Lỗi:**
| Code | Mô tả |
|------|-------|
| 401 | Email hoặc mật khẩu không đúng |

---

### GET `/auth/profile` 🔒 — Lấy thông tin cá nhân

**Response:**
```json
{
  "id": "uuid",
  "name": "Nguyễn Văn A",
  "email": "user@example.com"
}
```

---

## 2. Camera

### POST `/camera` 🔒 — Thêm camera

**Body:**
```json
{
  "name": "Camera sân phơi",
  "location": "Khu A"
}
```

**Response:**
```json
{
  "success": true,
  "camera_id": "uuid"
}
```

---

### GET `/camera` 🔒 — Danh sách camera của user

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Camera sân phơi",
    "location": "Khu A",
    "created_at": "2025-01-01 10:00:00"
  }
]
```

---

### GET `/camera/{id}` 🔒 — Chi tiết một camera

**Response:**
```json
{
  "id": "uuid",
  "name": "Camera sân phơi",
  "location": "Khu A",
  "created_at": "2025-01-01 10:00:00"
}
```

**Lỗi:**
| Code | Mô tả |
|------|-------|
| 404 | Camera không tồn tại |

---

### PUT `/camera/{id}` 🔒 — Cập nhật camera

**Body:**
```json
{
  "name": "Camera mới",
  "location": "Khu B"
}
```

**Response:**
```json
{ "success": true }
```

---

### DELETE `/camera/{id}` 🔒 — Xóa camera

**Response:**
```json
{ "success": true }
```

---

## 3. Sensor

> Không cần auth — ESP32 gọi trực tiếp.

### POST `/sensor` — Gửi dữ liệu cảm biến

**Body:**
```json
{
  "camera_id": "uuid",
  "temperature": 32.5,
  "humidity": 75.0
}
```

**Response:**
```json
{ "success": true }
```

---

### GET `/sensor/latest/{camera_id}` — Dữ liệu mới nhất

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "camera_id": "uuid",
    "temperature": 32.5,
    "humidity": 75.0,
    "recorded_at": "2025-01-01T10:00:00"
  }
}
```

> `data: null` nếu chưa có dữ liệu.

---

### GET `/sensor/history/{camera_id}?limit=50` — Lịch sử cảm biến

**Query params:**
| Param | Default | Mô tả |
|-------|---------|-------|
| `limit` | 50 | Số bản ghi tối đa |

**Response:**
```json
{
  "data": [ ... ]
}
```

---

## 4. Detection

> Không cần auth — dùng cho YOLO gửi kết quả.

### POST `/detection` — Lưu kết quả nhận diện

**Body:**
```json
{
  "camera_id": "uuid",
  "detected_count": 5,
  "confidence": 0.92
}
```

**Response:**
```json
{ "success": true }
```

---

### GET `/detection/latest/{camera_id}` — Kết quả mới nhất

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "camera_id": "uuid",
    "detected_count": 5,
    "confidence": 0.92,
    "detected_at": "2025-01-01T10:00:00"
  }
}
```

---

## 5. Prediction

> Không cần auth — dùng cho AI model gửi kết quả.

### POST `/prediction` — Lưu kết quả dự đoán thời gian khô

**Body:**
```json
{
  "camera_id": "uuid",
  "temperature": 32.5,
  "humidity": 75.0,
  "predicted_minutes": 45.0
}
```

**Response:**
```json
{ "success": true }
```

---

### GET `/prediction/latest/{camera_id}` — Dự đoán mới nhất

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "camera_id": "uuid",
    "temperature": 32.5,
    "humidity": 75.0,
    "predicted_minutes": 45.0,
    "created_at": "2025-01-01T10:00:00"
  }
}
```

---

## 6. Notification

### POST `/notification` — Tạo thông báo

**Body:**
```json
{
  "user_id": "uuid",
  "camera_id": "uuid",
  "weather_status": "high",
  "advice": "Khả năng mưa cao — thu bánh vào ngay"
}
```

**Response:**
```json
{ "success": true }
```

---

### GET `/notification/{user_id}` 🔒 — Lấy thông báo của user

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "camera_id": "uuid",
      "weather_status": "high",
      "advice": "Khả năng mưa cao — thu bánh vào ngay",
      "is_sent": false,
      "created_at": "2025-01-01T10:00:00"
    }
  ]
}
```

---

## 7. Dashboard

### GET `/dashboard/overview` 🔒 — Thống kê tổng quan

**Response:**
```json
{
  "total_users": 10,
  "total_cameras": 25,
  "total_detections": 1200,
  "total_predictions": 980
}
```

---

## 8. Weather AI

### GET `/weather/analyze` — Phân tích thời tiết + dự đoán mưa

**Query params:**
| Param | Default | Mô tả |
|-------|---------|-------|
| `lat` | `10.226` | Vĩ độ |
| `lon` | `106.421` | Kinh độ |
| `save` | `true` | Lưu vào DB |

**Response:**
```json
{
  "timestamp": "2025-01-01T10:00:00",
  "location": { "lat": 10.226, "lon": 106.421 },
  "api_weather": {
    "temperature_c": 32.5,
    "humidity_percent": 78,
    "pressure_hpa": 1010.2,
    "wind_speed_ms": 3.2,
    "precipitation_mm": 0.0,
    "weather_code": 2
  },
  "sensor_data": {
    "temperature_c": 33.1,
    "humidity_percent": 82.5,
    "source": "real_sensor"
  },
  "prediction": {
    "rain_score": 55.0,
    "rain_level": "medium",
    "rain_label": "Có thể có mưa",
    "max_precip_probability_12h": 60,
    "currently_raining": false
  },
  "advice": [
    "🌦️ Có thể có mưa — không nên phơi bánh tráng lúc này."
  ],
  "record_id": 42
}
```

---

## Ví dụ sử dụng (JavaScript)

```js
const BASE_URL = 'https://mylongaiv2.onrender.com'

// Đăng nhập
const res = await fetch(`${BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: '123456' })
})
const { access_token } = await res.json()

// Gọi API có auth
const cameras = await fetch(`${BASE_URL}/camera`, {
  headers: { 'Authorization': `Bearer ${access_token}` }
}).then(r => r.json())
```

---

## Lỗi chung

| Code | Mô tả |
|------|-------|
| 401 | Chưa đăng nhập hoặc token hết hạn |
| 404 | Không tìm thấy dữ liệu |
| 422 | Dữ liệu gửi lên không đúng định dạng |
| 500 | Lỗi server |
