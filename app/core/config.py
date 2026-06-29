from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "MyLongAI"
    DEBUG: bool = True
    DATABASE_URL: str = ""
    WEATHER_DATABASE_URL: str = ""
    GMAIL_USER: str = ""
    GMAIL_APP_PASSWORD: str = ""
    FRONTEND_URL: str = "https://batchguard-web.vercel.app"
    RESEND_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()