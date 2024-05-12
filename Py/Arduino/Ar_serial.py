from pydantic import BaseModel  
from fastapi.responses import FileResponse
import serial.tools.list_ports
from datetime import datetime, timezone, timedelta
import time
import os
import sqlite3
import threading
from device import device_data

class Database:
    def __init__(self) -> None:
        self.directory = '/home/jms/Documents/JMS_smart_farm/' # 우분투 기준
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        # check_same_thread 파라미터를 False로 설정
        self.conn = sqlite3.connect(self.directory + '/JMSPlant.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.check_and_insert_default_data()

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
        );

        CREATE TABLE IF NOT EXISTS ArduinoControl (
            idx INTEGER PRIMARY KEY AUTOINCREMENT,
            led BOOL,
            sysfan BOOL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            self.cursor.executescript(query)
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

    def check_and_insert_default_data(self):
        '''
        ArduinoControl 테이블에 데이터가 없는 경우 기본 데이터 삽입
        '''
        # 데이터가 있는지 확인
        self.cursor.execute("SELECT COUNT(*) FROM ArduinoControl")
        count = self.cursor.fetchone()[0]
        if count == 0:
            # 데이터가 없으면 기본 데이터 삽입
            query = "INSERT INTO ArduinoControl (led, sysfan, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)"
            # 기본값 예시: led와 sysfan을 False로 설정
            self.cursor.execute(query, (True, False))
            self.conn.commit()

    def smartFarm_insert_data(self, IsRun, sysfan, wpump, led, humidity, temperature, ground1, ground2) -> None:
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

    def send_data(self):
        '''
        데이터베이스에서 아두이노의 센서(LED, SYSFAN) 설정값을 가져와서 아두이노로 보냄
        '''
        self.db.cursor.execute("SELECT led, sysfan FROM ArduinoControl ORDER BY idx DESC LIMIT 1")
        result = self.db.cursor.fetchone()
        if result:
            led, sysfan = result
            # 아두이노로 보낼 메시지 구성
            message = f"{int(led)},{int(sysfan)}"
            # 시리얼 통신을 통해 아두이노로 메시지 보내기
            self.arduino.write(message.encode())
            
    def read_serial_data(self) -> str:
        '''
        아두이노에서 보낸 데이터를 data에 임시저장
        '''
        if self.arduino.in_waiting > 0:
            data = self.arduino.readline().decode().rstrip()
            return data

    def parse_data(self, data_line):
        # 데이터 타입에 따라 처리하는 함수 매핑
        data_handlers = {
            "IsRun": lambda x: bool(int(x)),
            "SYSFAN": lambda x: bool(int(x)),
            "WPUMP": lambda x: bool(int(x)),
            "LED": lambda x: bool(int(x)),
            "Humidity": lambda x: float(x.split("%")[0]),
            "Temperature": lambda x: float(x.split("*C")[0]),
            "Ground1": lambda x: round((int(x) / 1024) * 100, 1),
            "Ground2": lambda x: round((int(x) / 1024) * 100, 1),
        }

        key, value = data_line.split(":")
        key = key.strip()
        value = value.strip()

        # 데이터 핸들링 함수가 있는 경우, 해당 함수로 값 처리
        if key in data_handlers:
            return key, data_handlers[key](value)
        return key, value

    def read_data(self) -> None:
        '''
        아두이노에서 보낸 데이터를 파이썬에 변수로 저장, 출력
        '''
        data = self.read_serial_data()
        if data:
            key, value = self.parse_data(data)
            # 속성 이름을 동적으로 설정
            if hasattr(self, key.lower()):
                setattr(self, key.lower(), value)

            if time.time() - self.last_print_time >= 1:
                print(self.IsRun, self.sysfan, self.wpump, self.led, self.humidity, self.temperature, self.ground1, self.ground2)
                self.send_data()
                self.db.smartFarm_insert_data(self.IsRun, self.sysfan, self.wpump, self.led, self.humidity, self.temperature, self.ground1, self.ground2)
                self.last_print_time = time.time()  # 저장 시간을 업데이트

if __name__ == "__main__":
    Ar = Ardu()
    while True:
        Ar.read_data()    