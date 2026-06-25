from fastapi import APIRouter, Query, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from app.services.weather_service import get_weather_analysis
from app.services.weather_collector import save_weather_record, label_record, label_records_bulk, get_unlabeled, export_labeled_dataset
from app.services.auth_service import get_current_user
from fastapi import HTTPException

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/analyze")
async def weather_analyze(
    lat: float = Query(10.22649869822018, description="Vĩ độ"),
    lon: float = Query(106.42142282084475, description="Kinh độ"),
    save: bool = Query(True, description="Lưu vào DB để thu thập data"),
    current_user: dict = Depends(get_current_user)
):
    result = await get_weather_analysis(lat, lon)
    if save:
        record_id = save_weather_record(result)
        result["record_id"] = record_id

    is_premium = current_user.get("role") in ("premium", "admin")
    if not is_premium:
        result["advice"] = ["🔒 Nâng cấp Premium để nhận khuyến nghị phơi bánh tráng."]
    return result


class LabelRequest(BaseModel):
    record_id: int
    did_it_rain: bool

@router.post("/label")
def label_weather(body: LabelRequest):
    """Gán nhãn thực tế: có mưa hay không sau khi dự đoán"""
    success = label_record(body.record_id, body.did_it_rain)
    return {"success": success, "record_id": body.record_id, "did_it_rain": body.did_it_rain}


class BulkLabelRequest(BaseModel):
    labels: list[LabelRequest]

@router.post("/label/bulk")
def label_weather_bulk(body: BulkLabelRequest):
    """Gán nhãn hàng loạt"""
    result = label_records_bulk([{"record_id": l.record_id, "did_it_rain": l.did_it_rain} for l in body.labels])
    return result


@router.get("/unlabeled")
def unlabeled_records(limit: int = Query(50)):
    """Xem các record chưa được gán nhãn"""
    return get_unlabeled(limit)


@router.get("/dataset/export")
def export_dataset():
    """Xuất dataset đã có nhãn để train model"""
    data = export_labeled_dataset()
    return {"total": len(data), "records": data}
