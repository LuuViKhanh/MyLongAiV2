import asyncio
import httpx
import random
import time
from datetime import datetime, timedelta

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
SENSOR_API_URL = "https://mylongai-backend-sensors.onrender.com/sensor/latest"

_meteo_cache: dict = {}  # key: (lat, lon) -> {"data": ..., "expires": datetime}
CACHE_TTL_MINUTES = 10

# ==============================
# SENSOR DATA (thật + fallback mock)
# ==============================
async def get_sensor_data() -> dict:
    """Lấy nhiệt độ, độ ẩm thật từ thiết bị IoT. Fallback mock nếu lỗi."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(SENSOR_API_URL)
            resp.raise_for_status()
            raw = resp.json()

        if raw.get("status") != "success":
            raise ValueError("no sensor data")

        data = raw["data"]
        return {
            "temperature_c": data.get("temperature"),
            "humidity_percent": data.get("humidity"),
            "has_rice_paper": data.get("has_rice_paper"),
            "vision_confidence": data.get("vision_confidence"),
            "source": "real_sensor"
        }
    except Exception:
        # Fallback mock nếu sensor offline
        return {
            "temperature_c": round(random.uniform(24.0, 36.0), 1),
            "humidity_percent": round(random.uniform(55.0, 95.0), 1),
            "has_rice_paper": None,
            "vision_confidence": None,
            "source": "mock_sensor"
        }


# ==============================
# FETCH OPEN-METEO
# ==============================
async def fetch_open_meteo(lat: float, lon: float) -> dict:
    key = (round(lat, 3), round(lon, 3))
    cached = _meteo_cache.get(key)
    if cached and datetime.now() < cached["expires"]:
        return cached["data"]

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "surface_pressure",
            "wind_speed_10m",
            "precipitation",
            "weather_code"
        ],
        "hourly": ["precipitation_probability"],
        "forecast_days": 1,
        "timezone": "Asia/Ho_Chi_Minh"
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(OPEN_METEO_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        _meteo_cache[key] = {"data": data, "expires": datetime.now() + timedelta(minutes=CACHE_TTL_MINUTES)}
        return data
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            if cached:
                return cached["data"]  # dùng cache cũ dù đã hết hạn
            await asyncio.sleep(5)  # đợi 5s rồi thử lại 1 lần
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(OPEN_METEO_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
            _meteo_cache[key] = {"data": data, "expires": datetime.now() + timedelta(minutes=CACHE_TTL_MINUTES)}
            return data
        raise


# ==============================
# RAIN PREDICTION LOGIC
# ==============================
def predict_rain(meteo: dict, sensor: dict) -> dict:
    current = meteo.get("current", {})
    hourly = meteo.get("hourly", {})

    # Lấy xác suất mưa cao nhất trong 12h tới
    precip_probs = hourly.get("precipitation_probability", [0])[:12]
    max_precip_prob = max(precip_probs) if precip_probs else 0

    # Dữ liệu hiện tại từ Open-Meteo
    current_precip = current.get("precipitation", 0)
    weather_code = current.get("weather_code", 0)
    api_humidity = current.get("relative_humidity_2m", 0)
    api_wind_speed = current.get("wind_speed_10m", 0)
    # Kết hợp với sensor
    sensor_humidity = sensor["humidity_percent"]

    # Tính điểm nguy cơ mưa (0-100)
    score = 0
    score += min(max_precip_prob * 0.5, 50)                                          # API forecast: tối đa 50đ
    score += min((sensor_humidity - 60) * 1.2, 30) if sensor_humidity > 60 else 0   # Độ ẩm sensor cao
    score += 10 if current_precip > 0 else 0                                         # Đang có mưa
    score += 5 if weather_code in range(51, 100) else 0                              # WMO mưa/dông
    score += 5 if api_humidity > 85 else 0                                           # Độ ẩm khí tượng cao
    score += 5 if api_wind_speed > 5 else 0                                          # Gió mạnh

    score = round(min(score, 100), 1)

    # Phân loại
    if score >= 70:
        level = "high"
        rain_label = "Khả năng mưa cao"
    elif score >= 40:
        level = "medium"
        rain_label = "Có thể có mưa"
    else:
        level = "low"
        rain_label = "Ít khả năng mưa"

    return {
        "rain_score": score,
        "rain_level": level,
        "rain_label": rain_label,
        "max_precip_probability_12h": max_precip_prob,
        "currently_raining": current_precip > 0
    }


# ==============================
# ADVICE GENERATOR
# ==============================
def generate_advice(prediction: dict, sensor: dict) -> list[str]:
    advice = []
    level = prediction["rain_level"]
    humidity = sensor["humidity_percent"]
    temp = sensor["temperature_c"]

    if level == "high":
        advice.append("🌧️ Khả năng mưa cao — nên mang theo ô hoặc áo mưa.")
        advice.append("🚗 Hạn chế di chuyển nếu không cần thiết.")
    elif level == "medium":
        advice.append("🌦️ Có thể có mưa — nên chuẩn bị ô đề phòng.")
    else:
        advice.append("☀️ Thời tiết ổn định — ít khả năng mưa.")

    if humidity > 85:
        advice.append("💧 Độ ẩm rất cao — cảm giác oi bức, uống đủ nước.")
    if temp > 35:
        advice.append("🌡️ Nhiệt độ cao — tránh ra ngoài lúc 11h-15h.")
    if prediction["currently_raining"]:
        advice.append("☔ Hiện đang có mưa tại khu vực.")

    return advice


# ==============================
# MAIN SERVICE FUNCTION
# ==============================
async def get_weather_analysis(lat: float, lon: float) -> dict:
    meteo_data, sensor_data = await asyncio.gather(
        fetch_open_meteo(lat, lon),
        get_sensor_data()
    )
    prediction = predict_rain(meteo_data, sensor_data)
    advice = generate_advice(prediction, sensor_data)

    current = meteo_data.get("current", {})

    return {
        "timestamp": datetime.now().isoformat(),
        "location": {"lat": lat, "lon": lon},
        "api_weather": {
            "temperature_c": current.get("temperature_2m"),
            "humidity_percent": current.get("relative_humidity_2m"),
            "pressure_hpa": current.get("surface_pressure"),
            "wind_speed_ms": current.get("wind_speed_10m"),
            "precipitation_mm": current.get("precipitation"),
            "weather_code": current.get("weather_code")
        },
        "sensor_data": sensor_data,
        "prediction": prediction,
        "advice": advice
    }
