import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from collections import deque
import uvicorn
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import asyncio
from starlette.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# 사용자 요청을 저장할 대기열
user_queue = deque()

# 배치 처리를 위한 설정
batch_time = 5  # 요청을 배치로 처리할 시간 간격 (초 단위)

class LatestData(BaseModel):
    latest_temperature: float
    latest_humidity: float
    latest_ground1: float
    latest_ground2: float
    latest_sysfan: int
    latest_wpump: int
    latest_led: int
    created_at: datetime

class DB_Query():
    def __init__(self):
        self.client = AsyncIOMotorClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        self.db = self.client[os.getenv('DATABASE_NAME', 'JMSPlant')]
        self.collection = self.db.smartFarm

    async def fetch_latest_data(self):
        try:
            row = await self.collection.find().sort("created_at", -1).to_list(1)
            if row:
                return row[0]
            else:
                return None
        except Exception as e:
            logging.error(f"데이터베이스 쿼리 실행 중 오류 발생: {e}")
            return None

def get_db_query():
    db_query = DB_Query()
    try:
        yield db_query
    finally:
        db_query.client.close()

async def process_requests():
    while True:
        if user_queue:
            request = user_queue.popleft()
            # 여기서는 예시를 단순화하기 위해 요청을 로그로만 기록합니다.
            logging.info(f"처리된 요청: {request}")
        await asyncio.sleep(batch_time)  # 설정된 배치 시간만큼 대기

@app.on_event("startup")
async def startup_event():
    task = asyncio.create_task(process_requests())

@app.get("/api/latest", response_model=LatestData, summary="최근 데이터 조회")
async def get_latest_data(db_query: DB_Query = Depends(get_db_query)):
    global user_queue
    request = "latest_data_request"  # 실제 환경에서는 요청의 세부 정보를 포함시킬 수 있습니다.
    user_queue.append(request)  # 요청을 큐에 추가
    # 요청이 처리될 때까지 대기
    await asyncio.sleep(batch_time)
    
    logging.info("API /api/latest 호출됨")
    try:
        row = await db_query.fetch_latest_data()
        if row is None:
            raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
            
        data = LatestData(
            latest_temperature=row['temperature'],
            latest_humidity=row['humidity'],
            latest_ground1=row['ground1'],
            latest_ground2=row['ground2'],
            latest_sysfan=row['sysfan'],
            latest_wpump=row['wpump'],
            latest_led=row['led'],
            created_at=row['created_at'].strftime("%Y-%m-%d %H:%M:%S"))
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except IndexError:
        raise HTTPException(status_code=500)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
