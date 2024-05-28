from datetime import datetime, timedelta
from dotenv import load_dotenv
import sqlite3
import calendar
import requests
import logging
import os

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi

from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel, Field, field_validator
from jose import jwt

import uvicorn


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Smart Farm FastAPI",
        version="",
        summary="스마트팜 센서 데이터 전송 및 구글 API",
        description="최신 데이터ㅤㅤ=>ㅤget('/api/latest')\n\n"+
                    "인덱스 데이터ㅤ=>ㅤget('/api/idx100')\n\n"+
                    "시간별 데이터ㅤ=>ㅤpost('/api/hourly')\n\n"+
                    "주간별 데이터ㅤ=>ㅤpost('/api/week')\n\n"+
                    "월별 데이터ㅤㅤ=>ㅤpost('/api/month')\n\n"+
                    "ㅤ\n\n"+
                    "로그인 예제ㅤㅤ=>ㅤget('/login')\n\n"+
                    "로그인 주소ㅤㅤ=>ㅤpost('/login/google')\n\n"+
                    "계정 정보수집ㅤ=>ㅤpost('/auth/google')\n\n"+
                    "로그인 토큰ㅤㅤ=>ㅤpost('/token')",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://drive.google.com/thumbnail?id=112KMQN8u0iSUa-Wiwl2hAHwEEgNeSH1Q"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
app.openapi = custom_openapi
app.add_middleware(# CORS 미들웨어 추가
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()# 환경 변수 로드
templates = Jinja2Templates(directory="API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth = OAuth()# OAuth 클라이언트 설정
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url=os.getenv("GOOGLE_AUTH_URI"),
    authorize_params=None,
    access_token_url=os.getenv("GOOGLE_TOKEN_URI"),
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URIS"),
    client_kwargs={'scope': 'openid profile email'},
)

class DataRequest(BaseModel):
    date: str = Field(..., title="날짜",
                        description="날짜를 나타내는 문자열입니다. 1900-01-01에서 9999-12-31 사이의 값을 가져야 합니다.",)
    
    @field_validator('date')
    def check_date_range(cls, v):
        start_date = datetime.strptime("1900-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("9999-12-31", "%Y-%m-%d")
        input_date = datetime.strptime(v, "%Y-%m-%d")
        
        if not (start_date <= input_date <= end_date):
            raise ValueError(f"날짜는 1900-01-01에서 9999-12-31 사이의 값을 가져야 합니다. 입력된 날짜: {v}")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                "date": "2024-05-25"
                }
            ]
        }
    }
   
class WeekDataRequest(BaseModel):
    year: int = Field(..., title="년도", gt=1899, lt=10000,
                        description="년도를 나타내는 정수입니다. 1900에서 9999 사이의 값을 가져야 합니다.")
    month: int = Field(..., title="월", gt=0, lt=13,
                        description="월을 나타내는 정수입니다. 1에서 12 사이의 값을 가져야 합니다.")
    week: int = Field(..., title="주차", gt=0, lt=6,
                        description="주차를 나타내는 정수입니다. 1에서 5 사이의 값을 가져야 합니다.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                "year": 2024,
                "month": 5,
                "week": 1
                }
            ]
        }
    }

class MonthDataRequest(BaseModel):
    year: int = Field(..., title="년도", gt=1899, lt=10000,
                        description="년도를 나타내는 정수입니다. 1900에서 9999 사이의 값을 가져야 합니다.")
    month: int = Field(..., title="월", gt=0, lt=13,
                        description="월을 나타내는 정수입니다. 1에서 12 사이의 값을 가져야 합니다.")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                "year": 2024,
                "month": 5
                }
            ]
        }   
    }

class DB_Query():
    def __init__(self):
        self.DATABASE='JMSPlant.db'
        self.conn = None
        self.cursor = None
        self.query = ""

    def __enter__(self):
        '''self를 반환해서 with 문 내에서 사용할 수 있게 함'''
        self.conn = sqlite3.connect(self.DATABASE, check_same_thread=False)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): 
        '''리소스 누수를 방지용'''
        if self.conn:
            self.conn.close()
        if exc_type or exc_val or exc_tb:
            logging.error(f"데이터베이스 쿼리 실행 중 오류 발생: {exc_val}")
        return True  # 예외가 있어도 프로그램이 중단되지 않도록 함

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
        query = '''
            SELECT idx, sysfan, wpump, led, temperature, humidity, ground1, ground2, created_at
            FROM smartFarm
            ORDER BY created_at DESC LIMIT 1
        '''
        return self.execute_query(query)

    def fetch_recent_100_data(self):
        query = '''
            SELECT idx, temperature, humidity, ground1, ground2, created_at
            FROM smartFarm ORDER BY idx DESC LIMIT 100
        '''
        return self.execute_query(query)

    def fetch_hourly_data(self, checkdate: datetime):
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
        return self.execute_query(query)

    def fetch_weekly_data(self, checkdate: datetime):
        datequery = '''
            WHERE date(created_at) BETWEEN date('{}')
            AND date('{}', '+6 days')
            GROUP BY date(created_at)
            ORDER BY date(created_at) ASC
        '''
        query = '''
            SELECT idx, temperature, humidity, ground1, ground2, created_at
            FROM smartFarm
        ''' + datequery.format(checkdate, checkdate)
        return self.execute_query(query)

    def fetch_monthly_data(self, checkdate: datetime):
        datequery = '''
            WHERE date(created_at) BETWEEN date('{}')
            AND date('{}', '+30 days')
            GROUP BY date(created_at)
            ORDER BY date(created_at) ASC
        '''
        query = '''
            SELECT idx, temperature, humidity, ground1, ground2, created_at
            FROM smartFarm
        ''' + datequery.format(checkdate, checkdate)
        return self.execute_query(query)
        

def datetime_date(year: int, month: int, index: int = 0) -> datetime:
    '''
    해당 연도와 월에 대한 특정 주의 시작일과 그 달의 총 일수를 반환합니다.\n
    입력된 연도가 1900에서 9999 사이, 월이 1에서 12 사이가 아니면 None을 반환합니다.
    '''
    if (year < 1900 or year > 9999) or (month < 1 or month > 12):
        return None, None
    first_day_of_month, days_in_month = calendar.monthrange(year, month) # 해당 월의 1주차 시작일과 

    if first_day_of_month != 0:
        first_day_of_week = 8 - first_day_of_month
    else:
        first_day_of_week = 1

    start_day = first_day_of_week + ((index-1) * 7)
    check_date = f"{year}-{month:02d}-{start_day:02d}" # YYYY-MM-DD 형식으로변경
    if 0 >= start_day or days_in_month < start_day:
        return None, None
    return datetime.strptime(check_date, "%Y-%m-%d"), days_in_month


def datetime_days(date_list: list, rows: dict) -> list:
    '''
    주어진 날짜 목록에 대해 특정 데이터(온도, 습도, 지면 데이터)를 반환합니다.\n
    데이터가 있는 날짜의 경우 해당 데이터를, 데이터가 없는 날짜의 경우 None 값을 포함하는 딕셔너리를 리스트로 반환합니다.
    '''
    data_by_date = {datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S").date(): row for row in rows}
    data = []
    for date in date_list:
        if date.date() in data_by_date:
            row = data_by_date[date.date()]
            data.append({
                "temperature": row[1],
                "humidity": row[2],
                "ground1": row[3],
                "ground2": row[4],
                "created_at": row[5]
            })
        else:# 데이터가 없는 날짜는 None으로 설정
            data.append({
                "temperature": None,
                "humidity": None,
                "ground1": None,
                "ground2": None,
                "created_at": date.strftime("%Y-%m-%d %H:%M:%S")
            })
    return data

def get_db_query():
    '''DB_Query 클래스 의존성 생성 함수'''
    with DB_Query() as db:
        yield db

@app.get("/", summary="root 접속 시 docs 이동")
def root():
    return RedirectResponse(url="/docs")

@app.get("/api/latest", summary="최근 데이터 조회")
async def get_latest_data(db_query: DB_Query = Depends(get_db_query)):
    '''DB의 가장 최신 날짜의 데이터를 반환합니다.'''

    logging.info("API /api/latest 호출됨")
    rows = db_query.fetch_latest_data()
    if rows:
        data = [dict(Latest_temperature=row[4],
                    Latest_humidity=row[5],
                    Latest_ground1=row[6],
                    Latest_ground2=row[7],
                    Latest_sysfan=row[1],
                    Latest_wpump=row[2],
                    Latest_led=row[3],
                    Created_at=row[8]) for row in rows]
    
        return JSONResponse(content=data[0])
    else:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")
    
@app.get("/api/idx100", summary="idx 100 데이터 조회")
async def post_date_data(db_query: DB_Query = Depends(get_db_query)):
    '''DB의 idx필드의 최신 데이터 기준 내림차순 100개를 반환합니다.'''

    logging.info("API /api/date 호출됨")
    rows = db_query.fetch_recent_100_data()
    if rows:
        data = [dict(index=index,
                    Date_temperature=row[1],
                    Date_humidity=row[2],
                    Date_ground1=row[3],
                    Date_ground2=row[4],
                    Created_at=row[5]) for index, row in enumerate(rows)]
    
        return JSONResponse(content=data)
    else:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")
    
@app.post("/api/hourly", summary="시간 데이터 조회")
async def post_hourly_sensor_data(request_data: DataRequest, db_query: DB_Query = Depends(get_db_query)):
    '''
    yyyy-mm-dd형식의 날짜를 입력받아 해당 날짜의 시간 데이터를 반환합니다.\n\n
    Args:\n\n
    ㅤㅤdate (str): 날짜(yyyy-mm-dd)
    '''
    logging.info("API /api/hourly 호출됨")
    rows = db_query.fetch_hourly_data(checkdate=request_data.date)
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

@app.post("/api/week", summary="주간 데이터 조회")
async def post_data(request_data: WeekDataRequest, db_query: DB_Query = Depends(get_db_query)):
    '''
    년도, 월, 주차 정보를 입력받아 해당 날짜의 주간 데이터를 반환합니다.\n\n
    Args:\n\n
    ㅤㅤyear (int): 년도(yyyy)\n\n
    ㅤㅤmonth (int): 월(1 ~ 12)\n\n
    ㅤㅤweek (int): 주차(1 ~ 5)
    '''
    logging.info("API /api/week 호출됨")
    start_date, _ = datetime_date(request_data.year, request_data.month, request_data.week)
    if not start_date:
        raise HTTPException(status_code=400, detail="잘못된 날짜입니다.")  # 잘못된 요청에 대한 응답 코드 수정
    try:
        date_list = [start_date + timedelta(days=i) for i in range(7)] 
        rows = db_query.fetch_weekly_data(checkdate=start_date)
        data = datetime_days(date_list, rows)
        return JSONResponse(content=data)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except IndexError:
        raise HTTPException(status_code=500, detail="서버 내부 오류입니다.")
    except Exception:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")

    
@app.post("/api/month", summary="월간 데이터 조회")
async def post_month_data(request_data: MonthDataRequest, db_query: DB_Query = Depends(get_db_query)):
    '''
    년도, 월 정보를 입력받아 해당 날짜의 월간 데이터를 반환합니다.\n\n
    Args:\n\n
    ㅤㅤyear (int): 년도(yyyy)\n\n
    ㅤㅤmonth (int): 월(1 ~ 12)
    '''
    logging.info("API /api/month 호출됨")
    # date_str = f"{request_data.year}-{request_data.month:02d}-{1:02d}"
    start_date, days_in_month = datetime_date(request_data.year, request_data.month, index=1)
    try:
        date_list = [start_date + timedelta(days=i) for i in range(days_in_month)] 
        rows = db_query.fetch_monthly_data(checkdate=start_date)
        data = datetime_days(date_list, rows)
        return JSONResponse(content=data)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except IndexError:
        raise HTTPException(status_code=500, detail="서버 내부 오류입니다.")
    except Exception:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")


@app.get("/login", response_class=HTMLResponse, summary="구글 로그인 테스트")
async def get_login_html(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login/google", summary="구글 로그인 URL")
async def login_google():
    redirect_uris = os.getenv('GOOGLE_REDIRECT_URIS').split(',')
    redirect_uri = redirect_uris[0]
    url = (
        f"{os.getenv('GOOGLE_AUTH_URI')}?response_type=code"
        f"&client_id={os.getenv('GOOGLE_CLIENT_ID')}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=openid%20profile%20email"
        f"&access_type=offline"
    )
    return {"url": url}


@app.get("/auth/google", summary="구글 로그인 및 계정 정보")
async def auth_google(code: str):
    token_url = os.getenv("GOOGLE_TOKEN_URI")
    data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URIS").split(',')[0],
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch token")
    access_token = response.json().get("access_token")
    user_info_response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo",
                                        headers={"Authorization": f"Bearer {access_token}"})
    user_info = user_info_response.json()
    conn = sqlite3.connect('JMSPlant.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO user_info (id, email, verified_email, name, given_name, family_name, picture, locale)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_info.get("id"),
        user_info.get("email"),
        user_info.get("verified_email"),
        user_info.get("name"),
        user_info.get("given_name"),
        user_info.get("family_name", ""),  # 기본값을 빈 문자열로 설정
        user_info.get("picture"),
        user_info.get("locale")
    ))
    conn.commit()
    conn.close()
    return user_info

@app.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, os.getenv("GOOGLE_CLIENT_SECRET"), algorithms=["HS256"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)