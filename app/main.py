from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import ai_detect, ai_realtime, health, weather
from app.models.weather_record import create_tables

app = FastAPI(
    title="MyLongAI Backend",
    description="""
    Hệ thống AI Vision cho làng nghề MyLongAI
    
    Sử dụng YOLO để phân tích chất lượng sản phẩm.
    """,
    version="1.0.0"
)

create_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ dev thì để *, production thì giới hạn domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_detect.router, prefix="/ai", tags=["AI"])
app.include_router(ai_realtime.router, prefix="/ai", tags=["AI Realtime"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(weather.router, prefix="/weather", tags=["Weather AI"])
@app.get("/")
def root():
    return {"status": "ok"}