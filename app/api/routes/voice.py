from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from gtts import gTTS
import io

router = APIRouter()

RAIN_MESSAGES = {
    "high": "Cảnh báo! Khả năng mưa cao. Hãy thu bánh tráng vào ngay và tạm dừng sản xuất.",
    "medium": "Chú ý! Có thể có mưa. Không nên phơi bánh tráng lúc này.",
    "low": "Thời tiết ổn định. Thuận lợi để phơi bánh tráng."
}


@router.get("/alert")
def voice_alert(level: str = Query("medium", description="Mức độ mưa: low, medium, high")):
    text = RAIN_MESSAGES.get(level, RAIN_MESSAGES["medium"])
    tts = gTTS(text=text, lang="vi")
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="audio/mpeg")


@router.get("/custom")
def voice_custom(text: str = Query(..., description="Nội dung cần đọc bằng tiếng Việt")):
    tts = gTTS(text=text, lang="vi")
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="audio/mpeg")
