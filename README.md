# MyLongAI Backend v2

Backend dự báo thời tiết thông minh, kết hợp dữ liệu từ **cảm biến IoT thực tế** và **API khí tượng Open-Meteo** để dự đoán khả năng mưa và đưa ra lời khuyên.

**Production:** https://mylongaiv2.onrender.com

---

## Tính năng

- Lấy dữ liệu thời tiết thực từ [Open-Meteo](https://open-meteo.com/) (miễn phí, không cần API key)
- Kết hợp dữ liệu cảm biến IoT (nhiệt độ, độ ẩm) từ thiết bị thực
- Tính điểm nguy cơ mưa (0–100) dựa trên nhiều yếu tố
- Đưa ra lời khuyên thực tế (mang ô, tránh nắng,...)
- Thu thập và gán nhãn dữ liệu để train model AI sau này

---

## API Endpoints

Base URL: `https://mylongaiv2.onrender.com`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/` | Health check |
| GET | `/weather/analyze` | Phân tích thời tiết + dự đoán mưa |
| POST | `/weather/label` | Gán nhãn thực tế (có mưa hay không) |
| GET | `/weather/unlabeled` | Xem các record chưa gán nhãn |
| GET | `/weather/dataset/export` | Xuất dataset để train model |
| GET | `/docs` | Swagger UI - thử API trực tiếp |

---

## Chi tiết API

### GET `/weather/analyze`

Phân tích thời tiết tại một tọa độ.

**Query params:**

| Param | Type | Default | Mô tả |
|-------|------|---------|-------|
| `lat` | float | `10.226` | Vĩ độ |
| `lon` | float | `106.421` | Kinh độ |
| `save` | bool | `true` | Lưu vào DB để thu thập data |

**Ví dụ:**
```
GET /weather/analyze?lat=10.22649869822018&lon=106.42142282084475
```

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
    "has_rice_paper": null,
    "vision_confidence": null,
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
    "🌦️ Có thể có mưa — nên chuẩn bị ô đề phòng.",
    "💧 Độ ẩm rất cao — cảm giác oi bức, uống đủ nước."
  ],
  "record_id": 42
}
```

> `source: "real_sensor"` = dữ liệu thật từ IoT  
> `source: "mock_sensor"` = cảm biến offline, dùng dữ liệu giả

---

### POST `/weather/label`

Gán nhãn thực tế sau khi quan sát (dùng để thu thập training data).

**Body:**
```json
{
  "record_id": 42,
  "did_it_rain": true
}
```

**Response:**
```json
{
  "success": true,
  "record_id": 42,
  "did_it_rain": true
}
```

---

### GET `/weather/dataset/export`

Xuất toàn bộ dataset đã gán nhãn.

**Response:**
```json
{
  "total": 120,
  "records": [ ... ]
}
```

---

## Logic dự đoán mưa

Điểm nguy cơ mưa (0–100) được tính từ:

| Yếu tố | Điểm tối đa |
|--------|-------------|
| Xác suất mưa 12h tới (Open-Meteo) | 50 |
| Độ ẩm cảm biến IoT > 60% | 30 |
| Hiện đang có mưa | 10 |
| Mã thời tiết WMO (mưa/dông) | 5 |
| Độ ẩm khí tượng > 85% | 5 |
| Gió mạnh > 5 m/s | 5 |

| Điểm | Mức độ | Nhãn |
|------|--------|------|
| ≥ 70 | `high` | Khả năng mưa cao |
| 40–69 | `medium` | Có thể có mưa |
| < 40 | `low` | Ít khả năng mưa |

---

## Cài đặt & Chạy local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Tạo file `.env`:
```
MYSQL_URL=mysql+pymysql://<user>:<password>@<host>:<port>/<database>
```

Chạy server:
```bash
python run.py
```

Truy cập: http://localhost:8000/docs

---

## Cấu trúc project

```
app/
├── api/routes/
│   ├── health.py       # GET /
│   └── weather.py      # GET|POST /weather/*
├── services/
│   ├── weather_service.py    # Logic phân tích + dự đoán
│   └── weather_collector.py  # Lưu DB, gán nhãn, export
├── models/
│   └── weather_record.py     # SQLAlchemy model
├── core/
│   └── config.py       # Cấu hình từ .env
└── main.py
run.py                  # Entry point
```

---

## Tech Stack

- **FastAPI** - Web framework
- **Open-Meteo API** - Dữ liệu khí tượng (miễn phí)
- **SQLite / MySQL** - Lưu trữ dữ liệu thu thập
- **Render** - Hosting production
