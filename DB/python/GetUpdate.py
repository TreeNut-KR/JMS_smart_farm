from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import sqlite3
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="./Py/Arduino/templates")
# 데이터를 저장할 구조
class Data(BaseModel):
    IsRun: bool
    sysfan: bool
    wpump: bool
    led: bool
    humidity: float
    temperature: float
    ground1: int
    ground2: int

# 최신 데이터 조회 엔드포인트
@app.get("/latest_data")
async def get_latest_data():
    conn = sqlite3.connect('./JMSPlant.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM smartFarm ORDER BY idx DESC LIMIT 5
    ''')
    row = cursor.fetchone()
    conn.close()
    if row:
        data = {
            'Idx': row[0],
            'sysfan': row[2],
            'wpump': row[3],
            'led': row[4],
            'humidity': row[5],
            'temperature': row[6],
            'ground1': row[7],
            'ground2': row[8],
            'ground2': row[8],
            'created_at': row[9],
            'updated_at': row[10],
            'deleted_at': row[11],
        }
        return data
    else:
        raise HTTPException(status_code=404, detail="Data not found")

@app.get("/")
async def get_index_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 메인 함수
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8666)
