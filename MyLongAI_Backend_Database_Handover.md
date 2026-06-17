# MyLongAI Backend Database Handover

## 1. Kết nối Database

### File `.env`

```env
DATABASE_URL=postgresql://postgres.meeiuutsjkogjkpxbmef:TanMy%40huntrot@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres
```

### File `db.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "sslmode": "require"
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

---

## 2. Quy tắc làm việc

Database đã được tạo sẵn trên Supabase.

Backend KHÔNG được:

```sql
CREATE TABLE
ALTER TABLE
DROP TABLE
```

Backend chỉ sử dụng:

```sql
SELECT
INSERT
UPDATE
DELETE
```

---

## 3. Danh sách bảng

- users
- cameras
- sensor_readings
- detections
- drying_predictions
- notifications
- subscriptions

---

## 4. Quan hệ dữ liệu

```text
users
  |
  +----- cameras
             |
             +----- sensor_readings
             |
             +----- detections
             |
             +----- drying_predictions
             |
             +----- notifications

users
  |
  +----- subscriptions
```

---

## 5. Table users

Chức năng:

- Đăng ký
- Đăng nhập
- Phân quyền

Ví dụ lấy user:

```sql
SELECT *
FROM users
WHERE email = :email
```

---

## 6. Table cameras

Mỗi user có thể sở hữu nhiều camera.

Ví dụ:

```sql
SELECT *
FROM cameras
WHERE user_id = :user_id
```

---

## 7. Table sensor_readings

Dữ liệu ESP32 gửi lên.

API:

```http
POST /sensor
```

Insert:

```sql
INSERT INTO sensor_readings(
    id,
    camera_id,
    temperature,
    humidity
)
VALUES(
    gen_random_uuid(),
    :camera_id,
    :temperature,
    :humidity
)
```

Lấy dữ liệu mới nhất:

```sql
SELECT *
FROM sensor_readings
WHERE camera_id = :camera_id
ORDER BY recorded_at DESC
LIMIT 1
```

---

## 8. Table detections

Lưu kết quả YOLO Detect.

```sql
INSERT INTO detections(
    id,
    camera_id,
    detected_count,
    confidence
)
VALUES(
    gen_random_uuid(),
    :camera_id,
    :detected_count,
    :confidence
)
```

---

## 9. Table drying_predictions

Lưu kết quả AI dự đoán thời gian khô.

```sql
INSERT INTO drying_predictions(
    id,
    camera_id,
    temperature,
    humidity,
    predicted_minutes
)
VALUES(
    gen_random_uuid(),
    :camera_id,
    :temperature,
    :humidity,
    :predicted_minutes
)
```

---

## 10. Table notifications

Lưu cảnh báo thời tiết.

```sql
INSERT INTO notifications(
    id,
    user_id,
    camera_id,
    weather_status,
    advice,
    is_sent
)
VALUES(
    gen_random_uuid(),
    :user_id,
    :camera_id,
    :weather_status,
    :advice,
    false
)
```

---

## 11. Table subscriptions

Quản lý doanh thu.

```sql
INSERT INTO subscriptions(
    id,
    user_id,
    package_name,
    payment_status,
    amount
)
VALUES(
    gen_random_uuid(),
    :user_id,
    :package_name,
    :payment_status,
    :amount
)
```

---

## 12. API Backend cần triển khai

### Authentication

```http
POST /auth/register
POST /auth/login
GET /auth/profile
```

### Camera

```http
POST /camera
GET /camera
GET /camera/{id}
PUT /camera/{id}
DELETE /camera/{id}
```

### Sensor

```http
POST /sensor
GET /sensor/latest/{camera_id}
GET /sensor/history/{camera_id}
```

### Detection

```http
POST /detection
GET /detection/latest/{camera_id}
```

### Prediction

```http
POST /prediction
GET /prediction/latest/{camera_id}
```

### Notification

```http
POST /notification
GET /notification/{user_id}
```

### Dashboard

```http
GET /dashboard/overview
```

Ví dụ truy vấn:

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM cameras;
SELECT COUNT(*) FROM detections;
SELECT COUNT(*) FROM drying_predictions;
```

---

## 13. Lưu ý quan trọng

Prototype cũ sử dụng bảng:

```sql
sensor_logs
```

Bảng này KHÔNG nằm trong thiết kế chính thức.

Backend phải sử dụng:

- sensor_readings
- detections
- drying_predictions
- notifications

Không gom tất cả dữ liệu vào một bảng duy nhất.
