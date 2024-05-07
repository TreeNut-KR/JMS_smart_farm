from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import sqlite3
import uvicorn

app = FastAPI()

class DB_READ:
    def __init__(self):
        self.conn = sqlite3.connect('/home/jms/문서/JMS/JMS/JMSPlant.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def CURSOR(self, latest=False):
        # 공통 쿼리 부분
        query = '''
            SELECT idx, temperature, humidity, ground1, ground2 
            FROM smartFarm 
        '''
        if latest:
            # 최신 레코드 쿼리 확장
            query += 'ORDER BY created_at DESC LIMIT 1'
        else:
            # 모든 레코드 쿼리 확장
            query += 'WHERE date(created_at) <= date()'

        # 쿼리 실행
        self.cursor.execute(query)

    def READ(self, latest=False):
        try:
            self.CURSOR(latest)
            rows = self.cursor.fetchall()
            # 결과를 딕셔너리 형태로 변환
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
            # 오류 발생 시 예외 처리
            raise HTTPException(status_code=500, detail=f"에러발생: {str(e)}")
        finally:
            # 연결 종료
            self.conn.close()

# DB에서 데이터를 가져와서 키-값 형태로 반환하는 API 엔드포인트
@app.get("/api")
async def get_sensor_data():
    db_read = DB_READ()
    data = db_read.READ()
    return JSONResponse(content=data)

@app.get("/api/latest")
async def get_latest_sensor_data():
    db_read = DB_READ()
    data = db_read.READ(latest=True)
    if data:
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"message": "데이터가 없습니다."})

# 메인 함수
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
