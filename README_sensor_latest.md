# MyLongAI Sensor Server – API `/sensor/latest`

## Mục đích

API `/sensor/latest` dùng để lấy dữ liệu sensor mới nhất từ hệ thống MyLongAI.

Dữ liệu bao gồm:

- Nhiệt độ
- Độ ẩm
- Trạng thái có bánh tráng hay không
- Confidence từ AI Vision
- Timestamp của bản ghi mới nhất

API này phù hợp cho:

- Dashboard realtime
- AI prediction service
- Data analysis
- Frontend monitoring
- Testing hệ thống

---

# Endpoint

```text
GET /sensor/latest
```

Ví dụ:

```text
https://mylongai-backend-sensors.onrender.com/sensor/latest
```

---

# Method

```text
GET
```

---

# Response thành công

## Example Response

```json
{
  "status": "success",
  "data": {
    "timestamp": "2026-05-18T14:20:01.123456",
    "temperature": 31.5,
    "humidity": 72.1,
    "has_rice_paper": true,
    "vision_confidence": 0.93
  }
}
```

---

# Response Fields

| Field | Type | Description |
|---|---|---|
| status | string | API status |
| timestamp | datetime | Thời gian ghi nhận sensor |
| temperature | float | Nhiệt độ hiện tại (°C) |
| humidity | float | Độ ẩm hiện tại (%) |
| has_rice_paper | boolean | AI detect có bánh tráng hay không |
| vision_confidence | float | Độ tin cậy detect từ YOLO AI |

---

# Response khi chưa có dữ liệu

```json
{
  "status": "empty",
  "message": "no sensor data"
}
```

---

# Example Python

```python
import requests

url = "https://mylongai-backend-sensors.onrender.com/sensor/latest"

res = requests.get(url)

data = res.json()

print(data)
```

---

# Example JavaScript

```javascript
fetch("https://mylongai-backend-sensors.onrender.com/sensor/latest")
  .then(res => res.json())
  .then(data => {
    console.log(data);
  });
```

---

# Example Output

```text
Temperature: 31.5°C
Humidity: 72.1%
Rice Paper: True
Confidence: 0.93
```

---

# Realtime Usage Recommendation

Khuyến nghị polling mỗi:

```text
5–10 giây
```

để tránh spam server.

---

# Notes

## has_rice_paper

```text
true
```

→ Camera AI đang detect có bánh tráng.

```text
false
```

→ Không detect thấy bánh tráng.

---

## vision_confidence

Giá trị:

```text
0.0 → 1.0
```

Ví dụ:

```text
0.93
```

→ AI confidence 93%.

---

# Health Check

Có thể kiểm tra server hoạt động bằng:

```text
GET /health
```

Ví dụ:

```text
https://mylongai-backend-sensors.onrender.com/health
```

---

# Kiến trúc dữ liệu

```text
ESP32 Sensor
    ↓
POST /sensor

YOLO Camera AI
    ↓
POST /vision

Database PostgreSQL
    ↓
GET /sensor/latest
```

---

# Intended Use

API này được thiết kế cho:

- AI drying prediction
- Monitoring dashboard
- Data collection
- Real-time analytics
- Weather correlation analysis
- Batch tracking system
