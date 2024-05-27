from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from starlette.responses import RedirectResponse
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
import calendar
import sqlite3
import uvicorn
import logging
import re

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Smart Farm FastAPI",
        version="",
        description="스마트팜 센서 데이터 전송 API\n\n"+
                    "전체 데이터ㅤㅤ=>ㅤget('/api')\n\n"+
                    "최신 데이터ㅤㅤ=>ㅤget('/api/latest')\n\n"+
                    "시간별 데이터ㅤ=>ㅤpost('/api/hourly')\n\n"+
                    "일별 데이터ㅤㅤ=>ㅤpost('/api/date')\n\n"+
                    "주간별 데이터ㅤ=>ㅤpost('/api/week')\n\n"+
                    "월별 데이터ㅤㅤ=>ㅤpost('/api/month')",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI()
app.openapi = custom_openapi

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DataRequest(BaseModel):
    date: str = Field(..., title="날짜",
                        description="날짜를 나타내는 문자열입니다. 1900-01-01에서 9999-12-31 사이의 값을 가져야 합니다.",)
    @validator('date')
    def check_date_range(cls, v):
        start_date = datetime.strptime("1900-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("9999-12-31", "%Y-%m-%d")
        input_date = datetime.strptime(v, "%Y-%m-%d")
        
        if not (start_date <= input_date <= end_date):
            print(ValueError(f"날짜는 1900-01-01에서 9999-12-31 사이의 값을 가져야 합니다. 입력된 날짜: {v}"))
            raise ValueError(f"날짜는 1900-01-01에서 9999-12-31 사이의 값을 가져야 합니다. 입력된 날짜: {v}")
        return v
class WeekDataRequest(BaseModel):
    year: int = Field(...,title="년도", gt=1899, lt=10000,
                        description="년도를 나타내는 정수입니다. 1900에서 9999 사이의 값을 가져야 합니다.")
    month: int = Field(..., title="월", gt=0, lt=13,
                        description="월을 나타내는 정수입니다. 1에서 12 사이의 값을 가져야 합니다.")
    week: int = Field(..., title="주차", gt=0, lt=6,
                        description="주차을 나타내는 정수입니다. 1에서 5 사이의 값을 가져야 합니다.")
class MonthDataRequest(BaseModel):
    year: int = Field(..., title="년도", gt=1899, lt=10000,
                        description="년도를 나타내는 정수입니다. 1900에서 9999 사이의 값을 가져야 합니다.")
    month: int = Field(..., title="월", gt=0, lt=13,
                        description="월을 나타내는 정수입니다. 1에서 12 사이의 값을 가져야 합니다.")
    


def get_db_connection(DB: str = './JMSPlant.db'):
    return sqlite3.connect(DB, check_same_thread=False)

def week_date(year: int, month: int, week_index: int = 0) -> datetime:
    if year < 1900 or year > 9999:
        return None
    if month < 1 or month > 12:
        return None
    
    first_day_of_month, days_in_month = calendar.monthrange(year, month)

    if first_day_of_month != 0:
        first_day_of_week = 8 - first_day_of_month
    else:
        first_day_of_week = 1

    week_start_day = first_day_of_week + ((week_index-1) * 7)
    check_date = f"{year}-{month:02d}-{week_start_day:02d}" # YYYY-MM-DD 형식으로변경
    if 0 >= week_start_day or days_in_month < week_start_day:
        return None
    return datetime.strptime(check_date, "%Y-%m-%d")

def week_days(start_date: datetime, days: int, control: int) -> list:
    if days < 1 or days > 31:
        return None
    if control < 1 or control > 5:
        return None
    
    date_list = [start_date + timedelta(days=i) for i in range(days)]

    rows = execute_read_query(control=control, checkdate=start_date.strftime("%Y-%m-%d"))
    data_by_date = {datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S").date(): row for row in rows}

    # 데이터가 없는 날짜는 None으로 설정
    data = []
    for date in date_list:
        if date.date() in data_by_date:
            row = data_by_date[date.date()]
            data.append({
                "Week_temperature": row[1],
                "Week_humidity": row[2],
                "Week_ground1": row[3],
                "Week_ground2": row[4],
                "created_at": row[5]
            })
        else:
            data.append({
                "Week_temperature": None,
                "Week_humidity": None,
                "Week_ground1": None,
                "Week_ground2": None,
                "created_at": date.strftime("%Y-%m-%d %H:%M:%S")
            })
    return data

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
        datequery = "WHERE date(created_at) = date('{}')"
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

    elif control == 5:
        datequery = """
            WITH RECURSIVE hours AS (
                SELECT 0 AS hour
                UNION ALL
                SELECT hour + 1
                FROM hours
                WHERE hour < 23
            ),
            hour_data AS (
                SELECT
                    *,
                    strftime('%H', created_at) AS hour,
                    ROW_NUMBER() OVER (PARTITION BY strftime('%H', created_at) ORDER BY created_at ASC) as row_num
                FROM
                    smartFarm
                WHERE
                    DATE(created_at) = '{}'
            )
            SELECT
                strftime('%H', '{}', hours.hour || ' hours') AS hour_slot,
                hd.idx, hd.temperature, hd.humidity, hd.ground1, hd.ground2, hd.created_at
            FROM
                hours
            LEFT JOIN
                hour_data hd ON hours.hour = CAST(hd.hour AS INTEGER) AND hd.row_num = 1
            ORDER BY
                hour_slot;
        """
        query = datequery.format(checkdate, checkdate)

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        logging.info("데이터베이스 쿼리 실행")
    except:
        return
    return rows


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logging.error(f"ValueError: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "잘못된 값이 입력되었습니다."},
    )

@app.exception_handler(IndexError)
async def index_error_handler(request: Request, exc: IndexError):
    logging.error(f"IndexError: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류입니다."},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.error(f"Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "일반적인 예외가 발생했습니다."},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={"detail": "안녕하세요반갑습니다"},
    )


@app.get("/", summary="root 접속 시 docs 이동")
def root():
    return RedirectResponse(url="/docs")

@app.get("/docs", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="My FastAPI App - ReDoc"
    )

@app.get("/api", summary="전체 데이터 조회")
async def get_data():
    '''
    DB의 데이터를 모두 반환합니다.
    '''
    logging.info("API /api 호출됨")
    rows = execute_read_query(control=0, checkdate=None)
    if rows:
        data = [dict(All_temperature=row[1],
                    All_humidity=row[2],
                    All_ground1=row[3],
                    All_ground2=row[4],
                    Created_at=row[5]) for row in rows]
    
        return JSONResponse(content=data)
    else:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")

@app.get("/api/latest", summary="최근 데이터 조회")
async def get_latest_data():
    '''
    DB의 가장 최신 날짜의 데이터를 반환합니다.
    '''
    logging.info("API /api/latest 호출됨")
    rows = execute_read_query(control=1, checkdate = None)
    if rows:
        data = [dict(Latest_temperature=row[1],
                    Latest_humidity=row[2],
                    Latest_ground1=row[3],
                    Latest_ground2=row[4],
                    Created_at=row[5]) for row in rows]
    
        return JSONResponse(content=data[0])
    else:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")
    
@app.post("/api/hourly", response_model=DataRequest, summary="시간 데이터 조회")
async def post_hourly_sensor_data(request_data: DataRequest):
    '''
    yyyy-mm-dd형식의 날짜를 입력받아 해당 날짜의 시간 데이터를 반환합니다.

    Args:\n\n
    ㅤㅤdate (str): 날짜(yyyy-mm-dd)

    예제 요청:
    {
        "date": 2024-05-25
    }
    '''
    logging.info("API /api/hourly 호출됨")
    rows = execute_read_query(control=5, checkdate=request_data.date)
    if rows:
        data = [dict(Hour_slot=row[0],
                    Hourly_temperature=row[2],
                    Hourly_humidity=row[3],
                    Hourly_ground1=row[4],
                    Hourly_ground2=row[5],
                    Created_at=row[6]) for row in rows]
        return JSONResponse(content=data)
    else:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")

@app.post("/api/date", response_model=DataRequest, summary="일간 데이터 조회")
async def post_date_data(request_data : DataRequest):
    '''
    yyyy-mm-dd형식의 날짜를 입력받아 해당 날짜의 일간 데이터를 반환합니다.

    Args:\n\n
    ㅤㅤdate (str): 날짜(yyyy-mm-dd)

    예제 요청:
    {
        "date": 2024-05-25
    }
    '''
    logging.info("API /api/date 호출됨")
    rows = execute_read_query(control=2, checkdate = request_data.date)
    if rows:
        data = [dict(Date_temperature=row[1],
                    Date_humidity=row[2],
                    Date_ground1=row[3],
                    Date_ground2=row[4],
                    Created_at=row[5]) for row in rows]
    
        return JSONResponse(content=data)
    else:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")

@app.post("/api/week", response_model=WeekDataRequest, summary="주간 데이터 조회")
async def post_week_data(request_data: WeekDataRequest):
    '''
    년도, 월, 주차 정보를 입력받아 해당 날짜의 주간 데이터를 반환합니다.

    Args:\n\n
    ㅤㅤyear (int): 년도(yyyy)\n\n
    ㅤㅤmonth (int): 월(1 ~ 12)\n\n
    ㅤㅤweek (int): 주차(1 ~ 5)

    예제 요청:
    {
        "year": 2024,
        "month": 5
        "week": 1
    }
    '''
    logging.info("API /api/week 호출됨")
    start_date = week_date(request_data.year, request_data.month, request_data.week)
    if not start_date:
        raise HTTPException(status_code=400, detail="잘못된 날짜입니다.")  # 잘못된 요청에 대한 응답 코드 수정
    try:
        data = week_days(start_date, days=7, control=3)
        return JSONResponse(content=data)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except IndexError:
        raise HTTPException(status_code=500, detail="서버 내부 오류입니다.")
    except Exception:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")

    
@app.post("/api/month", response_model=MonthDataRequest, summary="월간 데이터 조회")
async def post_month_data(request_data: MonthDataRequest):
    '''
    년도, 월 정보를 입력받아 해당 날짜의 월간 데이터를 반환합니다.

    Args:\n\n
    ㅤㅤyear (int): 년도(yyyy)\n\n
    ㅤㅤmonth (int): 월(1 ~ 12)

    예제 요청:
    {
        "year": 2024,
        "month": 5
    }
    '''
    logging.info("API /api/month 호출됨")
    date_str = f"{request_data.year}-{request_data.month:02d}-{1:02d}"
    start_date = datetime.strptime(date_str, "%Y-%m-%d")
    # try:
    data = week_days(start_date, days=30, control=4)
    return JSONResponse(content=data)
    # except ValueError as ve:
    #     raise HTTPException(status_code=400, detail=str(ve))
    # except IndexError:
    #     raise HTTPException(status_code=500, detail="서버 내부 오류입니다.")
    # except Exception:
    #     raise HTTPException(status_code=404, detail="데이터가 없습니다.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)