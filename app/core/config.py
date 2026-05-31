from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "MyLongAI"
    DEBUG: bool = True
    MODEL_PATH: str = "app/models/my_model.pt"
    MAX_IMAGE_SIZE: int = 2 * 1024 * 1024  # 2MB
    MYSQL_URL: str = "mysql+pymysql://root:password@localhost:3306/weather_db"

    class Config:
        env_file = ".env"

settings = Settings()