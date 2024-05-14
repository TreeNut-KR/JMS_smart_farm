from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import sqlite3
import uvicorn
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JMSUpdate(BaseModel):
    LED : bool
    SYSFAN : bool

def get_db_connection():
    return sqlite3.connect('./JMSPlant.db', check_same_thread=False)

def execute_read_query(control):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT idx, temperature, humidity, ground1, ground2, created_at 
        FROM smartFarm 
    '''

    if control == 0:
        print("전체 데이터 출력")
        query += 'WHERE date(created_at) <= date()'
    elif control == 1:
        print("최신 데이터 출력")
        query += 'ORDER BY created_at DESC LIMIT 1'
    elif control == 2:
        print("7일 데이터 출력")
        query += "WHERE date(created_at) BETWEEN date('now', '-7 days') AND date('now')"
        
    cursor.execute(query)
    logging.info("데이터베이스 쿼리 실행")
    rows = cursor.fetchall()
    conn.close()
    return rows

def execute_update_query(LED, SYSFAN):
    conn = get_db_connection()
    cursor = conn.cursor()
    updated_at = datetime.now()  # 현재 시간을 가져옵니다.
    query = "UPDATE ArduinoControl SET LED = ?, SYSFAN = ?, updated_at = ? WHERE idx = 1"
    cursor.execute(query, (LED, SYSFAN, updated_at))
    conn.commit()
    conn.close()
    logging.info("데이터베이스 쿼리 실행")

@app.get("/api")
async def get_sensor_data():
    logging.info("API /api 호출됨")
    rows = execute_read_query(control=0)
    data = [dict(temperature=row[1], humidity=row[2], ground1=row[3], ground2=row[4], ceated_at=row[5]) for row in rows]
    if data:
        return data
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})

@app.get("/api/latest")
async def get_latest_sensor_data():
    logging.info("API /api/latest 호출됨")
    rows = execute_read_query(control=1)
    data = [dict(temperature=row[1], humidity=row[2], ground1=row[3], ground2=row[4]) for row in rows]
    if data:
        return data[0]
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})
    
@app.get("/api/week")
async def get_week_sensor_data():
    logging.info("API /api/week 호출됨")
    rows = execute_read_query(control=2)
    data = [dict(temperature=row[1], humidity=row[2], ground1=row[3], ground2=row[4]) for row in rows]
    if data:
        return data[0]
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})
    
@app.post("/api/senddata")
async def post_control_data(JMS: JMSUpdate):
    logging.info("API /api/senddata 호출됨")
    execute_update_query(JMS.LED, JMS.SYSFAN)
    return JSONResponse(content={"message": "데이터베이스에 요청사항이 적용되었습니다."})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
