from datetime import datetime, timedelta
from dotenv import load_dotenv
import sqlite3
import calendar
import requests
import logging
import os

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi

from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from jose import jwt
from fastapi_login import LoginManager
from datetime import timedelta

import uvicorn

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
templates = Jinja2Templates(directory="API/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth = OAuth()# OAuth 클라이언트 설정
oauth_data = {
    'name': 'google',
    'client_id': os.getenv("GOOGLE_CLIENT_ID"),
    'client_secret': os.getenv("GOOGLE_CLIENT_SECRET"),
    'authorize_url': os.getenv("GOOGLE_AUTH_URI"),
    'authorize_params': None,
    'access_token_url': os.getenv("GOOGLE_TOKEN_URI"),
    'access_token_params': None,
    'refresh_token_url': None,
    'redirect_uri': os.getenv("GOOGLE_REDIRECT_URIS"),
    'client_kwargs': {'scope': 'openid profile email'}
}
oauth.register(**oauth_data)

# 세션 비밀키 설정
SECRET = os.getenv("SESSION_SECRET")
manager = LoginManager(SECRET, token_url="/auth/token")

class User(BaseModel):
    username: str

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
class latestData(BaseModel):
    latest_temperature: float
    latest_humidity: float
    latest_ground1: int
    latest_ground2: int
    latest_sysfan: int
    latest_wpump: int
    latest_led: int
    created_at: datetime 
class idx100Data(BaseModel):
    index: int
    Date_temperature: float
    Date_humidity: float
    Date_ground1: int
    Date_ground2: int
    Created_at: datetime 
class hourData(BaseModel):
    Hour_slot: str
    Hourly_temperature:  Optional[float]
    Hourly_humidity:  Optional[float]
    Hourly_ground1:  Optional[int]
    Hourly_ground2: Optional[int]
    Created_at: Optional[datetime]
class daysData(BaseModel):
    temperature: Optional[float]
    humidity: Optional[float]
    ground1: Optional[int]
    ground2: Optional[int]
    created_at: Optional[datetime]
class Google_URL(BaseModel):
    url: str

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    '''400 오류처리'''
    logging.error(f"ValueError: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "잘못된 값이 입력되었습니다."},
    )
@app.exception_handler(IndexError)
async def index_error_handler(request: Request, exc: IndexError):
    '''500 오류처리'''
    logging.error(f"IndexError: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류입니다."},
    )
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    '''따로 설정한 오류 외에 다른 오류 발생시 출력'''
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
async def not_found_handler(request: Request, exc: HTTPException):
    '''404 오류처리'''
    return JSONResponse(
        status_code=404,
        content={"detail": "데이터를 불러오지 못했습니다."},
    )
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: HTTPException):
    '''422 오류처리'''
    return JSONResponse(
        status_code=422,
        content={"detail": "잘못된 입력값입니다"},
    )
@app.exception_handler(424)
async def failed_dependency_handler(request: Request, exc: HTTPException):
    '''424 오류처리'''
    return JSONResponse(
        status_code=424,
        content={"detail": "의존성 실패로 요청이 처리되지 않았습니다"},
    )
@app.exception_handler(429)
async def too_many_requests_handler(request: Request, exc: HTTPException):
    '''429 오류처리'''
    return JSONResponse(
        status_code=429,
        content={"detail": "요청이 너무 많습니다"},
    )
@app.exception_handler(502)
async def bad_gateway_handler(request: Request, exc: HTTPException):
    '''502 오류처리'''
    return JSONResponse(
        status_code=502,
        content={"detail": "게이트웨이 오류가 발생했습니다"},
    )

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
        query = self.query + " ORDER BY created_at DESC LIMIT 1"
        return self.execute_query(query)

    def fetch_recent_100_data(self):
        query = self.query + " ORDER BY idx ASC LIMIT 100"
        return self.execute_query(query)

    def fetch_hourly_data(self, checkdate: datetime):
        query = """
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
        """.format(checkdate, checkdate)
        return self.execute_query(query)

    def fetch_weekly_data(self, checkdate: datetime):
        query =self.query + '''
            WHERE date(created_at) BETWEEN date('{}')
            AND date('{}', '+6 days')
            GROUP BY date(created_at)
            ORDER BY date(created_at) ASC
        '''.format(checkdate, checkdate)
        return self.execute_query(query)

    def fetch_monthly_data(self, checkdate: datetime):
        query = self.query + '''
            WHERE date(created_at) BETWEEN date('{}')
            AND date('{}', '+30 days')
            GROUP BY date(created_at)
            ORDER BY date(created_at) ASC
        '''.format(checkdate, checkdate)
        return self.execute_query(query)
    
    def google_uesr_data(self, checkdate: dict):
        query = '''
        INSERT OR REPLACE INTO user_info (id, email, verified_email, name, given_name, family_name, picture, locale)
        VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
        '''.format(
            checkdate.get("id"),
            checkdate.get("email"),
            checkdate.get("verified_email"),
            checkdate.get("name"),
            checkdate.get("given_name"),
            checkdate.get("family_name", ""),
            checkdate.get("picture"),
            checkdate.get("locale")
        )
        self.cursor.execute(query)
        self.conn.commit()
        self.conn.close()

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
async def root():
    return RedirectResponse(url="/docs")
    
@app.get("/example")
async def example_endpoint():
    # 429 에러를 강제로 발생시키는 예제
    raise HTTPException(status_code=429)

@app.post("/example/{status_code}")
async def example(status_code: int):
    if status_code in [400, 500, 404, 422, 424, 429, 502]:
        raise HTTPException(status_code=status_code)
    return {"message": "Invalid status code"}

@app.get("/api/latest", response_model=latestData, summary="최근 데이터 조회")
async def get_latest_data(db_query: DB_Query = Depends(get_db_query)):
    '''
    가장 최신 날짜의 데이터를 반환합니다.
    '''
    logging.info("API /api/latest 호출됨")
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
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except IndexError:
        raise HTTPException(status_code=500)
    except Exception:
        raise HTTPException(status_code=404)

@app.get("/api/idx100", response_model=List[idx100Data], summary="idx 100 데이터 조회")
async def get_recent_100_data(db_query: DB_Query = Depends(get_db_query)):
    '''
    idx필드의 최신 데이터 기준 내림차순 100개를 반환합니다.
    '''
    logging.info("API /api/idx100 호출됨")
    try:
        rows = db_query.fetch_recent_100_data()
        data = [idx100Data(
                index=index,
                Date_temperature=row[1],
                Date_humidity=row[2],
                Date_ground1=row[3],
                Date_ground2=row[4],
                Created_at=row[5]
            ) for index, row in enumerate(rows)]
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except IndexError:
        raise HTTPException(status_code=500)
    except Exception:
        raise HTTPException(status_code=404)
    
@app.post("/api/hourly", response_model=List[hourData], summary="시간 데이터 조회")
async def post_hourly_sensor_data(request_data: DataRequest, db_query: DB_Query = Depends(get_db_query)):
    '''
    yyyy-mm-dd 형식의 날짜를 입력받아 해당 날짜의 시간 데이터를 반환합니다.
    '''
    logging.info("API /api/hourly 호출됨")
    try:
        rows = db_query.fetch_hourly_data(checkdate=request_data.date)
        data = [hourData(
                Hour_slot=row[0],
                Hourly_temperature=row[2],
                Hourly_humidity=row[3],
                Hourly_ground1=row[4],
                Hourly_ground2=row[5],
                Created_at=row[6]
            ) for row in rows]
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except IndexError:
        raise HTTPException(status_code=500)
    except Exception:
        raise HTTPException(status_code=404)

@app.post("/api/week", response_model=List[daysData], summary="주간 데이터 조회")
async def post_data(request_data: WeekDataRequest, db_query: DB_Query = Depends(get_db_query)):
    '''
    년도, 월, 주차 정보를 입력받아 해당 날짜의 주간 데이터를 반환합니다.
    '''
    logging.info("API /api/week 호출됨")
    start_date, _ = datetime_date(request_data.year, request_data.month, request_data.week)
    if not start_date:
        raise HTTPException(status_code=400)  # 잘못된 요청에 대한 응답 코드 수정
    try:
        date_list = [start_date + timedelta(days=i) for i in range(7)]
        rows = db_query.fetch_weekly_data(checkdate=start_date)
        data = datetime_days(date_list, rows)
        return JSONResponse(content=data)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except IndexError:
        raise HTTPException(status_code=500)
    except Exception:
        raise HTTPException(status_code=404)

    
@app.post("/api/month", response_model=List[daysData], summary="월간 데이터 조회")
async def post_month_data(request_data: MonthDataRequest, db_query: DB_Query = Depends(get_db_query)):
    '''
    년도, 월 정보를 입력받아 해당 날짜의 월간 데이터를 반환합니다.
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
        raise HTTPException(status_code=500)
    except Exception:
        raise HTTPException(status_code=404)

@app.get("/login", response_class=HTMLResponse, summary="구글 로그인 테스트")
async def get_login_html(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login/google", response_model=Google_URL, summary="구글 로그인 URL")
async def login_google():
    url = (
        f"{oauth_data['authorize_url']}?response_type=code"
        f"&client_id={oauth_data['client_id']}"
        f"&redirect_uri={oauth_data['redirect_uri']}"
        f"&scope=openid%20profile%20email"
        f"&access_type=offline"
    )
    return Google_URL(url=url)


@app.get("/auth/google", summary="구글 로그인 및 계정 정보")
async def auth_google(code: str, db_query: DB_Query = Depends(get_db_query)):
    token_url = oauth_data['access_token_url']
    data = {
        "code": code,
        "client_id": oauth_data['client_id'],
        "client_secret": oauth_data['client_secret'],
        "redirect_uri": oauth_data['redirect_uri'],
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch token")
    access_token = response.json().get("access_token")
    user_info_response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo",
                                        headers={"Authorization": f"Bearer {access_token}"})
    user_info = user_info_response.json()
    db_query.google_uesr_data(user_info)

    # 세션 생성
    user = User(username=user_info['email'])
    # 액세스 토큰에 만료 시간을 1시간으로 설정
    access_token = manager.create_access_token(
        data={"sub": user.username},
        expires=timedelta(hours=1)
    )

    return {"detail": "Success"}

@app.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, os.getenv("GOOGLE_CLIENT_SECRET"), algorithms=["HS256"])

if __name__ == "__main__":
    # uvicorn.run("complexed_chart:app", host="0.0.0.0", port=8000,  reload=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)