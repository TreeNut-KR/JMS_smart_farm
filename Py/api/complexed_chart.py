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
        #DB 연결 경로 수정해야함
        self.conn = sqlite3.connect('C:/JMS_SmartFarm_API/JMS_smart_farm/DB/20240213/JMSPlant_remake.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def CURSOR(self, control):
        query = '''
            SELECT id, temperature, humidity, ground1, ground2 
            FROM ardu_data 
        '''

        if control == 0:
            print("전체 데이터 출력")
            query += 'WHERE date(time) <= date()'
        elif control == 1:
            print("최신 데이터 출력")
            query += 'ORDER BY time DESC LIMIT 1'
        elif control == 2:
            print("7일 데이터 출력")
            query += "WHERE date(time) BETWEEN date('now', '-3 days') AND date('now')"
            
        self.cursor.execute(query)
        logging.info("데이터베이스 쿼리 실행")  # 로그 기록 추가

    def READ(self, control=False):
        try:
            self.CURSOR(control)
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

class DB_SEND:
    def __init__(self):
        #DB 연결 경로 수정해야함
        self.conn = sqlite3.connect('C:\JMS_SmartFarm_API\JMS_smart_farm\DB\JMSPlant.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
    
    def CURSOR(self, LED, SYSFAN):
        qurey = '''
            INSERT INTO ArduinoControl (led, sysfan) VALUES (?, ?)
        '''
        self.cursor.execute(qurey, (LED, SYSFAN))
        self.conn.commit()
        logging.info("데이터베이스 쿼리 실행")  # 로그 기록 추가

    def SEND(self, LED, SYSFAN):
        try:
            self.CURSOR(LED, SYSFAN)
        except Exception as e:
            logging.error(f"데이터베이스 읽기 오류: {str(e)}")  # 오류 로그 추가
            raise HTTPException(status_code=500, detail=f"에러발생: {str(e)}")
        finally:
            self.conn.close()
            return 1


#DB 내 모든 데이터 출력
@app.get("/api")
async def get_sensor_data():
    logging.info("API /api 호출됨")  # 로그 기록
    db_read = DB_READ()
    data = db_read.READ(control=0)
    if data:
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})

#DB 내 최신 데이터 1개 출력
@app.get("/api/latest")
async def get_latest_sensor_data():
    logging.info("API /api/latest 호출됨")  # 로그 기록
    db_read = DB_READ()
    data = db_read.READ(control=1)
    if data:
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})
    
#DB 내 최근 1주간 데이터 출력
@app.get("/api/week")
async def get_latest_sensor_data():
    logging.info("API /api/all 호출됨")  # 로그 기록
    db_read = DB_READ()
    data = db_read.READ(latest=2)
    if data:
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})
    
#센서 제어 데이터를 DB에 추가
@app.post("/api/senddata")
async def post_control_data(LED : int, SYSFAN : int):
    logging.info("API /api/senddata 호출됨") #로그 기록
    db_send = DB_SEND()
    data = db_send.SEND(LED, SYSFAN)
    if data:
        return JSONResponse(content={"message": "데이터베이스에 요청사항이 적용되었습니다."})
    else:
        return JSONResponse(content={"message": "요청사항이 적용되지 않았습니다."})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)