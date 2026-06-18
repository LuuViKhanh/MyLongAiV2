from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.api.routes import health, weather, auth, camera, sensor, detection, prediction, notification, dashboard, users, subscriptions, iot

app = FastAPI(
    title="MyLongAI Backend",
    description="""
    Hệ thống AI Vision cho làng nghề MyLongAI

    Sử dụng YOLO để phân tích chất lượng sản phẩm.

    **Hướng dẫn dùng Swagger:**
    1. Gọi `POST /auth/login` lấy `access_token`
    2. Click nút **Authorize** 🔒 góc trên phải
    3. Nhập `Bearer <access_token>` rồi click Authorize
    """,
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://mylongaiv2.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(weather.router, prefix="/weather", tags=["Weather AI"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(camera.router, prefix="/camera", tags=["Camera"])
app.include_router(sensor.router, prefix="/sensor", tags=["Sensor"])
app.include_router(detection.router, prefix="/detection", tags=["Detection"])
app.include_router(prediction.router, prefix="/prediction", tags=["Prediction"])
app.include_router(notification.router, prefix="/notification", tags=["Notification"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(users.router, prefix="/users", tags=["User Management (Admin)"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["Revenue (Admin)"])
app.include_router(iot.router, prefix="/iot", tags=["IoT & AI Internal"])
@app.get("/")
def root():
    return {"status": "ok"}