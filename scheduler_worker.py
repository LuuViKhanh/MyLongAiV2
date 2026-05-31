"""
Worker thu thập data thời tiết — chạy trên Render 24/7
"""
import asyncio
import httpx
from datetime import datetime

API_URL = "https://your-app-name.onrender.com/weather/analyze"  # đổi thành URL Render của bạn
INTERVAL_SECONDS = 900  # 15 phút

async def collect():
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(API_URL, params={"lat": 10.22649869822018, "lon": 106.42142282084475})
        data = resp.json()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] "
              f"record_id={data.get('record_id')} "
              f"rain_level={data['prediction']['rain_level']} "
              f"score={data['prediction']['rain_score']}")

async def main():
    print("Worker started — thu thập data 24/7...")
    while True:
        try:
            await collect()
        except Exception as e:
            print(f"Lỗi: {e}")
        await asyncio.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main())
