import uvicorn
import os
from app.models.weather_record import create_tables

if __name__ == "__main__":
    create_tables()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port
    )