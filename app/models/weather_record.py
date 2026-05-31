from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id              = Column(Integer, primary_key=True, index=True)
    timestamp       = Column(DateTime, default=datetime.now)
    lat             = Column(Float)
    lon             = Column(Float)

    # Từ Open-Meteo
    api_temperature = Column(Float)
    api_humidity    = Column(Float)
    api_pressure    = Column(Float)
    api_wind_speed  = Column(Float)
    api_precipitation = Column(Float)
    api_weather_code  = Column(Integer)
    api_precip_prob_max = Column(Float)   # xác suất mưa cao nhất 12h

    # Từ sensor (mock hoặc thật)
    sensor_temperature = Column(Float)
    sensor_humidity    = Column(Float)
    sensor_source      = Column(String(20))  # real_sensor hoặc mock_sensor

    # Kết quả dự đoán
    rain_score  = Column(Float)
    rain_level  = Column(String(20))

    # Nhãn thực tế — cập nhật sau (NULL = chưa có)
    did_it_rain = Column(Boolean, nullable=True, default=None)


from app.core.config import settings

engine = create_engine(settings.MYSQL_URL)
SessionLocal = sessionmaker(bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)
