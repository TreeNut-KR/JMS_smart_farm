import os
import sqlite3
import logging
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from collections import deque
import uvicorn
from pydantic import BaseModel
import asyncio  # 비동기 처리를 위해 추가
app = FastAPI()

# 사용자 입장 요청을 저장할 대기열
user_queue = deque()

class latestData(BaseModel):
    latest_temperature: float
    latest_humidity: float
    latest_ground1: float
    latest_ground2: float
    latest_sysfan: int
    latest_wpump: int
    latest_led: int
    created_at: str

class DB_Query():
    def __init__(self):
        self.DATABASE = os.getenv('DATABASE', 'JMSPlant.db')
        self.conn = None
        self.cursor = None
        self.query = '''
            SELECT idx, temperature, humidity, ground1, ground2, created_at, sysfan, wpump, led
            FROM smartFarm
            '''

    def __enter__(self):
        self.conn = sqlite3.connect(self.DATABASE, check_same_thread=False)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        if exc_type or exc_val or exc_tb:
            logging.error(f"데이터베이스 쿼리 실행 중 오류 발생: {exc_val}")
        return True

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            logging.info("데이터베이스 쿼리 실행")
            return rows
        except Exception as e:
            logging.error(f"데이터베이스 쿼리 실행 중 오류 발생: {e}")
            return []

    def fetch_latest_data(self):
        query = self.query + " ORDER BY created_at DESC LIMIT 1"
        return self.execute_query(query)

def get_db_query():
    with DB_Query() as db:
        yield db

# 대기열에서 요청을 처리하는 비동기 함수
async def process_queue():
    while True:
        if not user_queue:
            return
        db_query = user_queue.popleft()
        try:
            rows = db_query.fetch_latest_data()
            data = latestData(
                latest_temperature=rows[0][1],
                latest_humidity=rows[0][2],
                latest_ground1=rows[0][3],
                latest_ground2=rows[0][4],
                latest_sysfan=rows[0][6],
                latest_wpump=rows[0][7],
                latest_led=rows[0][8],
                created_at=rows[0][5])
            return data  # 처리 결과 반환
        except Exception as e:
            logging.error(f"대기열 처리 중 오류 발생: {e}")
        await asyncio.sleep(1)  # 다음 요청 처리까지 잠시 대기

@app.get("/api/latest", response_model=latestData, summary="최근 데이터 조회")
async def get_latest_data(db_query: DB_Query = Depends(get_db_query)):
    logging.info("API /api/latest 호출됨")
    user_queue.append(db_query)  # 요청을 큐에 추가
    return await process_queue()  # 대기열에서 요청 처리 및 결과 반환

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)