# API Documentation — MyLongAI Backend

Base URL: `https://mylongaiv2.onrender.com`

Swagger UI: `https://mylongaiv2.onrender.com/docs`

---

## Xác thực

Các API có ký hiệu 🔒 yêu cầu Bearer Token trong header:

```
Authorization: Bearer <access_token>
```

Các API có ký hiệu 👑 chỉ dành cho **Admin**.

Token lấy từ `POST /auth/login`.

---

## Danh sách API

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| POST | `/auth/register` | | Đăng ký |
| POST | `/auth/login` | | Đăng nhập |
| GET | `/auth/profile` | 🔒 | Thông tin cá nhân |
| POST | `/camera` | 🔒 | Thêm camera |
| GET | `/camera` | 🔒 | Danh sách camera |
| GET | `/camera/{id}` | 🔒 | Chi tiết camera |
| PUT | `/camera/{id}` | 🔒 | Cập nhật camera |
| DELETE | `/camera/{id}` | 🔒 | Xóa camera |
| POST | `/sensor` | | Gửi dữ liệu cảm biến |
| GET | `/sensor/latest/{camera_id}` | | Dữ liệu cảm biến mới nhất |
| GET | `/sensor/history/{camera_id}` | | Lịch sử cảm biến |
| POST | `/detection` | | Lưu kết quả nhận diện |
| GET | `/detection/latest/{camera_id}` | | Kết quả nhận diện mới nhất |
| POST | `/prediction` | | Lưu kết quả dự đoán khô |
| GET | `/prediction/latest/{camera_id}` | | Dự đoán khô mới nhất |
| POST | `/notification` | | Tạo thông báo |
| GET | `/notification/{user_id}` | 🔒 | Thông báo của user |
| GET | `/dashboard/overview` | 👑 | Tổng quan cũ |
| GET | `/dashboard/admin` | 👑 | Dashboard admin |
| GET | `/dashboard/admin/confidence-chart` | 👑 | Biểu đồ AI Detect |
| GET | `/dashboard/admin/dryness-chart` | 👑 | Biểu đồ Dryness |
| GET | `/users` | 👑 | Danh sách user |
| GET | `/users/{id}` | 👑 | Chi tiết user |
| PATCH | `/users/{id}/disable` | 👑 | Khóa user |
| PATCH | `/users/{id}/enable` | 👑 | Mở khóa user |
| GET | `/subscriptions` | 👑 | Danh sách giao dịch |
| GET | `/subscriptions/statistics` | 👑 | Thống kê doanh thu |
| POST | `/iot/sensor-data` | | ESP32 gửi sensor |
| POST | `/iot/detection-result` | | AI ghi kết quả detect |
| POST | `/iot/dryness-result` | | AI ghi kết quả dryness |
| GET | `/weather/analyze` | | Phân tích thời tiết |

---

## 1. Auth

### POST `/auth/register`

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

| Code | Mô tả |
|------|-------|
| 400 | Email đã được đăng ký |

---

### POST `/auth/login`

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
  "name": "Nguyễn Văn A",
  "role": "customer"
}
```

> Lưu `access_token` để dùng cho các API có 🔒

| Code | Mô tả |
|------|-------|
| 401 | Email hoặc mật khẩu không đúng |

---

### GET `/auth/profile` 🔒

**Response:**
```json
{
  "id": "uuid",
  "name": "Nguyễn Văn A",
  "email": "user@example.com",
  "role": "customer"
}
```

---

## 2. Camera

### POST `/camera` 🔒

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

### GET `/camera` 🔒

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

### GET `/camera/{id}` 🔒

**Response:**
```json
{
  "id": "uuid",
  "name": "Camera sân phơi",
  "location": "Khu A",
  "created_at": "2025-01-01 10:00:00"
}
```

---

### PUT `/camera/{id}` 🔒

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

### DELETE `/camera/{id}` 🔒

**Response:**
```json
{ "success": true }
```

---

## 3. Sensor

> Không cần auth — ESP32 có thể gọi trực tiếp.

### POST `/sensor`

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

### GET `/sensor/latest/{camera_id}`

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

### GET `/sensor/history/{camera_id}?limit=50`

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

### POST `/detection`

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

### GET `/detection/latest/{camera_id}`

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

### POST `/prediction`

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

### GET `/prediction/latest/{camera_id}`

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

### POST `/notification`

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

### GET `/notification/{user_id}` 🔒

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

## 7. Dashboard Admin 👑

### GET `/dashboard/admin`

**Response:**
```json
{
  "customer_count": 25,
  "camera_count": 80,
  "online_camera_count": 72,
  "total_revenue": 15000000
}
```

---

### GET `/dashboard/admin/confidence-chart`

Biểu đồ độ chính xác AI Detect theo ngày (30 ngày gần nhất).

**Response:**
```json
{
  "data": [
    {
      "date": "2025-01-01",
      "avg_confidence": 0.91,
      "total_detected": 120
    }
  ]
}
```

---

### GET `/dashboard/admin/dryness-chart`

Biểu đồ thời gian khô trung bình theo ngày (30 ngày gần nhất).

**Response:**
```json
{
  "data": [
    {
      "date": "2025-01-01",
      "avg_minutes": 45.5,
      "avg_humidity": 72.3,
      "avg_temperature": 33.1
    }
  ]
}
```

---

## 8. User Management 👑

### GET `/users`

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "full_name": "Nguyễn Văn A",
      "email": "user@example.com",
      "role": "customer",
      "last_login": "2025-01-01T10:00:00",
      "created_at": "2025-01-01T08:00:00"
    }
  ]
}
```

---

### GET `/users/{id}`

**Response:**
```json
{
  "id": "uuid",
  "full_name": "Nguyễn Văn A",
  "email": "user@example.com",
  "role": "customer",
  "last_login": "2025-01-01T10:00:00",
  "created_at": "2025-01-01T08:00:00"
}
```

---

### PATCH `/users/{id}/disable`

Khóa user (set role = `disabled`). Không thể khóa admin.

**Response:**
```json
{
  "success": true,
  "user_id": "uuid",
  "status": "disabled"
}
```

---

### PATCH `/users/{id}/enable`

Mở khóa user (set role = `customer`).

**Response:**
```json
{
  "success": true,
  "user_id": "uuid",
  "status": "enabled"
}
```

---

## 9. Revenue 👑

### GET `/subscriptions`

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "package_name": "Pro",
      "payment_status": "paid",
      "amount": 500000,
      "transaction_time": "2025-01-01T10:00:00"
    }
  ]
}
```

---

### GET `/subscriptions/statistics`

**Response:**
```json
{
  "today": 500000,
  "month": 15000000,
  "year": 120000000
}
```

---

## 10. IoT & AI Internal

> Frontend không gọi các API này. Dành cho ESP32 và AI model.

### POST `/iot/sensor-data`

ESP32 gửi nhiệt độ và độ ẩm.

**Body:**
```json
{
  "camera_id": "uuid",
  "temperature": 32.5,
  "humidity": 75.0
}
```

---

### POST `/iot/detection-result`

AI YOLO ghi kết quả nhận diện.

**Body:**
```json
{
  "camera_id": "uuid",
  "detected_count": 5,
  "confidence": 0.92
}
```

---

### POST `/iot/dryness-result`

AI ghi kết quả dự đoán thời gian khô.

**Body:**
```json
{
  "camera_id": "uuid",
  "temperature": 32.5,
  "humidity": 75.0,
  "predicted_minutes": 45.0
}
```

---

## 11. Weather AI

### GET `/weather/analyze`

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
const { access_token } = await fetch(`${BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: '123456' })
}).then(r => r.json())

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
| 403 | Không có quyền (cần Admin) |
| 404 | Không tìm thấy dữ liệu |
| 422 | Dữ liệu gửi lên không đúng định dạng |
| 500 | Lỗi server |
