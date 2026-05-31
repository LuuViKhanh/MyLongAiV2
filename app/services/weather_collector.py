from app.models.weather_record import WeatherRecord, SessionLocal

def save_weather_record(analysis: dict) -> int:
    """Lưu kết quả phân tích vào DB, trả về record id"""
    db = SessionLocal()
    try:
        api = analysis["api_weather"]
        sensor = analysis["sensor_data"]
        pred = analysis["prediction"]

        record = WeatherRecord(
            lat=analysis["location"]["lat"],
            lon=analysis["location"]["lon"],

            api_temperature=api.get("temperature_c"),
            api_humidity=api.get("humidity_percent"),
            api_pressure=api.get("pressure_hpa"),
            api_wind_speed=api.get("wind_speed_ms"),
            api_precipitation=api.get("precipitation_mm"),
            api_weather_code=api.get("weather_code"),
            api_precip_prob_max=pred.get("max_precip_probability_12h"),

            sensor_temperature=sensor.get("temperature_c"),
            sensor_humidity=sensor.get("humidity_percent"),
            sensor_source=sensor.get("source"),

            rain_score=pred.get("rain_score"),
            rain_level=pred.get("rain_level"),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    finally:
        db.close()


def label_record(record_id: int, did_it_rain: bool) -> bool:
    """Cập nhật nhãn thực tế cho một record"""
    db = SessionLocal()
    try:
        record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
        if not record:
            return False
        record.did_it_rain = did_it_rain
        db.commit()
        return True
    finally:
        db.close()


def get_unlabeled(limit: int = 50) -> list:
    """Lấy các record chưa có nhãn — dùng để gán nhãn hàng loạt"""
    db = SessionLocal()
    try:
        rows = db.query(WeatherRecord).filter(WeatherRecord.did_it_rain == None).limit(limit).all()
        return [{"id": r.id, "timestamp": r.timestamp, "rain_score": r.rain_score, "rain_level": r.rain_level} for r in rows]
    finally:
        db.close()


def export_labeled_dataset() -> list:
    """Xuất toàn bộ data đã có nhãn để train model"""
    db = SessionLocal()
    try:
        rows = db.query(WeatherRecord).filter(WeatherRecord.did_it_rain != None).all()
        return [
            {
                "api_temperature": r.api_temperature,
                "api_humidity": r.api_humidity,
                "api_pressure": r.api_pressure,
                "api_wind_speed": r.api_wind_speed,
                "api_precipitation": r.api_precipitation,
                "api_weather_code": r.api_weather_code,
                "api_precip_prob_max": r.api_precip_prob_max,
                "sensor_temperature": r.sensor_temperature,
                "sensor_humidity": r.sensor_humidity,
                "did_it_rain": r.did_it_rain,
            }
            for r in rows
        ]
    finally:
        db.close()
