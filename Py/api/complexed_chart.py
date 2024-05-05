from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import sqlite3
from datetime import datetime

app = FastAPI()

# DB에서 데이터를 가져와서 키-값 형태로 반환하는 API 엔드포인트
@app.get("/api")
async def get_sensor_data():
    conn = sqlite3.connect('/home/jms/Documents/JMS/JMSPlant.db')
    cursor = conn.cursor()
    
    try:
        # 쿼리 실행
        cursor.execute('''
            SELECT idx, temp_sensor, humidity_sensor, soil_sensor1, soil_sensor2 
            FROM smartFarm 
            WHERE created_at <= date()
        ''')
        rows = cursor.fetchall()
        
        # 결과를 딕셔너리 형태로 변환
        data = {}
        for row in rows:
            data[row[0]] = {
                'temperature': row[1],
                'humidity': row[2],
                'soil_sensor1': row[3],
                'soil_sensor2': row[4]
            }
        
        # JSONResponse로 반환
        return JSONResponse(content=data)
    
    except Exception as e:
        # 오류 발생 시 예외 처리
        raise HTTPException(status_code=500, detail=f"에러발생: {str(e)}")
    
    finally:
        # 연결 종료
        conn.close()

# 메인 함수
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)