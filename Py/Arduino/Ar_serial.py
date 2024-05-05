from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  
from fastapi.responses import FileResponse
import serial.tools.list_ports
from datetime import datetime, timezone, timedelta
import time
import uvicorn
import threading
import mysql.connector
from device import device_data

app = FastAPI()

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

class Database:
    def __init__(self) -> None:
        # MySQL 데이터베이스 연결 설정
        # 여기서 user, password, host, database를 자신의 환경에 맞게 수정해야 합니다.
        self.conn = mysql.connector.connect(
            user='root',
            password='1234',
            host='localhost',
            database='jmedu'
        )
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        '''
        DB 테이블 생성
        '''
        query = """
        CREATE TABLE IF NOT EXISTS smartFarm (
            idx INTEGER PRIMARY KEY AUTOINCREMENT,
            IsRun BOOL,
            sysfan BOOL,
            wpump BOOL,
            led BOOL,
            humidity REAL,
            temperature REAL,
            ground1 INTEGER,
            ground2 INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP DEFAULT NULL
        )
        """
        self.cursor.execute(query)

    def insert_data(self, IsRun, sysfan, wpump, led, humidity, temperature, ground1, ground2) -> None:
        '''
        DB에 데이터 삽입
        '''
        current_time = datetime.now(timezone(timedelta(hours=9)))
        current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
        query = """
        INSERT INTO smartFarm (IsRun, sysfan, wpump, led, humidity, temperature, ground1, ground2,created_at,updated_at,deleted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """
        self.cursor.execute(query, (IsRun, sysfan, wpump, led, humidity, temperature, ground1, ground2,current_time_str, current_time_str))
        self.conn.commit()


class Ardu(device_data):
    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.port = self.ar_get("USB")
        self.arduino = None
        self.defl = "0"

        self.IsRun = None
        self.sysfan = None
        self.wpump = None
        self.led = None
        self.humidity = None
        self.temperature = None
        self.ground1 = None
        self.ground2 = None
        self.a =1
        self.last_print_time = time.time()

        try:
            self.arduino = serial.Serial(self.port , 9600)
        except Exception as e:
            print(f"Port Error: {e}")
            exit(1)
        time.sleep(2)

    def send_data(self) -> None:
        '''
        파이썬에서 아두이노의 센서(LED, SYSFAN)를 설정
        '''
        input_1, input_2 = map(str, input("\n1. LED, 2. FAN\n(on : 1, off : 0)\ninput : ").split())
        sendDATA = input_1 + ',' + input_2
        self.arduino.write(sendDATA.encode())

    def read_serial_data(self) -> str:
        '''
        아두이노에서 보낸 데이터를 data에 임시저장
        '''
        if self.arduino.in_waiting > 0:
            data = self.arduino.readline().decode().rstrip()
            return data

    def read_data(self) -> None:
        '''
        아두이노에서 보낸 데이터를 파이썬에 변수로 저장, 출력
        '''
        data = self.read_serial_data()
        if data:
            if data.startswith("IsRun : "):
                if(int(data.split(":")[1].strip()) == 1):
                    self.IsRun          = True
                else:
                    self.IsRun          = False
            if data.startswith("SYSFAN : "):
                if(int(data.split(":")[1].strip()) == 1):
                    self.sysfan         = True
                else:
                    self.sysfan         = False
            if data.startswith("WPUMP : "):
                if(int(data.split(":")[1].strip()) == 1):
                    self.wpump          = True
                else:
                    self.wpump          = False
            if data.startswith("LED : "):
                if(int(data.split(":")[1].strip()) == 1):
                    self.led            = True
                else:
                    self.led            = False
            if data.startswith("Humidity : "):
                self.humidity       = float(data.split(":")[1].strip().split("%")[0])
            if data.startswith("Temperature : "):
                self.temperature    = float(data.split(":")[1].strip().split("*C")[0])
            if data.startswith("Ground1 :"):
                self.ground1        = int(data.split(":")[1].strip())
            if data.startswith("Ground2 :"):
                self.ground2        = int(data.split(":")[1].strip())
            # Check if it has been more than 1 second since last print
            if time.time() - self.last_print_time >= 1:#저장시간
                #print(f"Received data - \nIsRun: {self.IsRun}, SYSFAN: {self.sysfan}, WPUMP: {self.wpump}, Humidity: {self.humidity}%, Temperature: {self.temperature}°C, Ground1: {self.ground1}, Ground2: {self.ground2}")
                self.db.insert_data(self.IsRun, self.sysfan, self.wpump, self.led, self.humidity, self.temperature, self.ground1, self.ground2)
                self.last_print_time = time.time()  # Update the last print time

    def MultiProcessing_Read_Data(self) -> None:
        '''
        수신 데이터 멀티쓰레드
        '''
        while True:
            self.read_data()

    def MultiProcessing_Send_Data(self) -> None:
        # '''
        # 송신 데이터 멀티쓰레드
        # '''
        # while True:
        #     try:
        #         self.send_data()
        #     except:
        #         print("\nRetry\n")
        uvicorn.run(app, host="0.0.0.0", port=8666)

# 최신 데이터 조회 엔드포인트
def get_database_connection():
    try:
        conn = mysql.connector.connect(
            user='root',
            password='1234',
            host='localhost',
            database='jmedu'
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        # 실제 운영 환경에서는 예외를 적절히 처리하는 방식을 고려해야 합니다.
        # 여기서는 예시로 print만 하고 있습니다.
        return None

@app.get("/latest_data")
async def get_latest_data():
    conn = get_database_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM smartFarm ORDER BY idx DESC LIMIT 1
    ''')
    row = cursor.fetchone()
    conn.close()
    if row:
        data = {
            'IsRun': row[1],
            'sysfan': row[2],
            'wpump': row[3],
            'led': row[4],
            'humidity': row[5],
            'temperature': row[6],
            'ground1': row[7],
            'ground2': row[8],
            'created_at': row[9],
            'updated_at': row[10],
            'deleted_at': row[11],
        }
        return data
    else:
        raise HTTPException(status_code=404, detail="Data not found")

# 기본 경로('/')로 접속했을 때 index.html 반환
@app.get("/")
async def get_index_html():
    return FileResponse("Py/Arduino/latest_data/index.html")

# 메인 함수
if __name__ == "__main__":
    Ar = Ardu()
    Ar.read_data()    
    read_process = threading.Thread(target = Ar.MultiProcessing_Read_Data)
    read_process.start()
    send_process =  threading.Thread(target = Ar.MultiProcessing_Send_Data)
    send_process.start()

    read_process.join()
    send_process.join()