from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "MyLongAI"
    DEBUG: bool = True
    MYSQL_URL: str = "mysql+pymysql://root:password@localhost:3306/weather_db"

    class Config:
        env_file = ".env"

settings = Settings()