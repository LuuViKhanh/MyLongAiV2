"""
Chạy song song với server để tự động thu thập data mỗi giờ.
Usage: python scheduler.py
"""
import asyncio
import httpx
from datetime import datetime

API_URL = "http://localhost:8000/weather/analyze"
INTERVAL_SECONDS = 600  # 15 phút

async def collect():
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(API_URL, params={"lat": 10.22649869822018, "lon": 106.42142282084475})
        data = resp.json()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] "
              f"record_id={data.get('record_id')} "
              f"rain_level={data['prediction']['rain_level']} "
              f"score={data['prediction']['rain_score']}")

async def main():
    print("Scheduler started — thu thập data mỗi giờ...")
    while True:
        try:
            await collect()
        except Exception as e:
            print(f"Lỗi: {e}")
        await asyncio.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main())
