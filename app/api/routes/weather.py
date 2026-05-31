from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.services.weather_service import get_weather_analysis
from app.services.weather_collector import save_weather_record, label_record, get_unlabeled, export_labeled_dataset

router = APIRouter()


@router.get("/analyze")
async def weather_analyze(
    lat: float = Query(10.22649869822018, description="Vĩ độ"),
    lon: float = Query(106.42142282084475, description="Kinh độ"),
    save: bool = Query(True, description="Lưu vào DB để thu thập data")
):
    result = await get_weather_analysis(lat, lon)
    if save:
        record_id = save_weather_record(result)
        result["record_id"] = record_id  # trả về để client dùng khi gán nhãn
    return result


class LabelRequest(BaseModel):
    record_id: int
    did_it_rain: bool

@router.post("/label")
def label_weather(body: LabelRequest):
    """Gán nhãn thực tế: có mưa hay không sau khi dự đoán"""
    success = label_record(body.record_id, body.did_it_rain)
    return {"success": success, "record_id": body.record_id, "did_it_rain": body.did_it_rain}


@router.get("/unlabeled")
def unlabeled_records(limit: int = Query(50)):
    """Xem các record chưa được gán nhãn"""
    return get_unlabeled(limit)


@router.get("/dataset/export")
def export_dataset():
    """Xuất dataset đã có nhãn để train model"""
    data = export_labeled_dataset()
    return {"total": len(data), "records": data}
