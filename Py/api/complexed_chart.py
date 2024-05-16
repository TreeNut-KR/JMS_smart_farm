from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import calendar
import math
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
    return sqlite3.connect('./JMSPlant_test.db', check_same_thread=False)

def get_week(year, month, week_index=0):
    '''
    Returns the first day of the specified week in the given month and year.
    
    Args:
        year (int): The year.
        month (int): The month.
        week_index (int, optional): The index of the week, starting from 0 (default is 0).
    
    Returns:
        datetime.datetime: The first day of the specified week, or None if the week index is out of range.
    '''
    first_day_of_month, days_in_month = calendar.monthrange(year, month)

    if first_day_of_month != 0:
        first_day_of_week = 8 - first_day_of_month
    else:
        first_day_of_week = 1

    week_start_day = first_day_of_week + (week_index * 7)
    check_date = f"{year}-{month:02d}-{week_start_day:02d}"

    if 0 >= week_start_day or days_in_month < week_start_day:
        return None
    return datetime.strptime(check_date, "%Y-%m-%d")

def execute_read_query(control, checkdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT idx, temperature, humidity, ground1, ground2, created_at 
        FROM smartFarm 
    '''
    if control == 0: # 전체 데이터 출력
        query += 'WHERE date(created_at) <= date()'

    elif control == 1: # 최신 데이터 출력
        query += 'ORDER BY created_at DESC LIMIT 1'

    elif control == 2: # 선택한 날짜의 데이터출력
        datequery = '''
            WHERE date(created_at) = date('{}')
            AND hour(created_at) IN (00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)
            AND minute(created_at) = 00
            AND second(created_at) = 00
            ORDER BY hour(created_at)

        '''
        query += datequery.format(checkdate)

    elif control == 3: # 선택한 주의 데이터출력
        datequery = ''' 
            WHERE date(created_at) BETWEEN date('{}') 
            AND date('{}', '+6 days') 
            GROUP BY date(created_at) 
            ORDER BY date(created_at) ASC
        '''# 선택한 날짜가 속한 주의 시작일(월요일)과 종료일(일요일)을 계산합니다.
        query += datequery.format(checkdate, checkdate)

    elif control == 4: # 선택한 달의 데이터출력
        datequery = '''
            WHERE date(created_at) BETWEEN date('{}') 
            AND date('{}', '+30 days') 
            GROUP BY date(created_at) 
            ORDER BY date(created_at) ASC
        '''
        query += datequery.format(checkdate, checkdate)
        
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        logging.info("데이터베이스 쿼리 실행")
    except:
        return 
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
    rows = execute_read_query(control=0, checkdate=None)

    data = [dict(All_temperature=row[1], 
                 All_humidity=row[2], 
                 All_ground1=row[3], 
                 All_ground2=row[4], 
                 ceated_at=row[5]) for row in rows]
    if data:
        return data
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})

@app.get("/api/latest")
async def get_latest_sensor_data():
    logging.info("API /api/latest 호출됨")
    rows = execute_read_query(control=1, checkdate = None)

    data = [dict(Latest_temperature=row[1], 
                 Latest_humidity=row[2], 
                 Latest_ground1=row[3], 
                 Latest_ground2=row[4], 
                 ceated_at=row[5]) for row in rows]
    if data:
        return data[0]
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})

#DB 내 선택한 날짜의 데이터 출력
@app.get("/api/date")
async def get_date_sensor_data(checkdate : str): # date?checkdate=yyyy-mm-dd
    logging.info("API /api/date 호출됨")  # 로그 기록
    rows = execute_read_query(control=2, checkdate = checkdate)
    print(rows)
    data = [dict(Date_temperature=row[1], 
                 Date_humidity=row[2], 
                 Date_ground1=row[3], 
                 Date_ground2=row[4], 
                 ceated_at=row[5]) for row in rows]
    if data:
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})

#DB 내 선택한 날짜가 해당하는 주의 데이터 출력
@app.get("/api/week")
async def get_week_sensor_data(year : int, month : int, week : int): # week?checkdate=yyyy-mm-dd
    logging.info("API /api/week 호출됨")  # 로그 기록
    checkdate = get_week(year, month, week)
    rows = execute_read_query(control=3, checkdate=checkdate)

    data = [dict(Week_temperature=row[1], 
                 Week_humidity=row[2], 
                 Week_ground1=row[3], 
                 Week_ground2=row[4], 
                 ceated_at=row[5]) for row in rows]
    if data:
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})
    
#DB 내 선택한 날짜가 해당하는 달의 데이터 출력
@app.get("/api/month")
async def get_month_sensor_data(checkdate : str): # month?checkdate=yyyy-mm-dd
    logging.info("API /api/month 호출됨")  # 로그 기록
    rows = execute_read_query(control=4, checkdate=checkdate)

    data = [dict(Month_temperature=row[1], 
                 Month_humidity=row[2], 
                 Month_ground1=row[3], 
                 Month_ground2=row[4], 
                 ceated_at=row[5]) for row in rows]
    if data:
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})

#센서 제어 데이터를 DB에 추가
@app.post("/api/senddata")
async def post_control_data(JMS: JMSUpdate):
    logging.info("API /api/senddata 호출됨")
    execute_update_query(JMS.LED, JMS.SYSFAN)
    return JSONResponse(content={"message": "데이터베이스에 요청사항이 적용되었습니다."})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
