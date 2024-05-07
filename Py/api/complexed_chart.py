from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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

class DB_READ:
    def __init__(self):
        self.conn = sqlite3.connect('/home/jms/문서/JMS/JMS/JMSPlant.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def CURSOR(self, latest=False):
        query = '''
            SELECT id, temperature, humidity, ground1, ground2 
            FROM ardu_data
        '''
        if latest:
            query += 'ORDER BY time DESC LIMIT 1'
        else:
            query += 'WHERE date(time) <= date()'
        self.cursor.execute(query)
        logging.info("데이터베이스 쿼리 실행")  # 로그 기록 추가

    def READ(self, latest=False):
        try:
            self.CURSOR(latest)
            rows = self.cursor.fetchall()
            data = {}
            for row in rows:
                data[row[0]] = {
                    'temperature': row[1],
                    'humidity': row[2],
                    'ground1': row[3],
                    'ground2': row[4]
                }
            return data
        except Exception as e:
            logging.error(f"데이터베이스 읽기 오류: {str(e)}")  # 오류 로그 추가
            raise HTTPException(status_code=500, detail=f"에러발생: {str(e)}")
        finally:
            self.conn.close()

@app.get("/api")
async def get_sensor_data():
    logging.info("API /api 호출됨")  # 로그 기록
    db_read = DB_READ()
    data = db_read.READ()
    if data:
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})

@app.get("/api/latest")
async def get_latest_sensor_data():
    logging.info("API /api/latest 호출됨")  # 로그 기록
    db_read = DB_READ()
    data = db_read.READ(latest=True)
    if data:
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
