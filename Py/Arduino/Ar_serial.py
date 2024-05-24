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
        self.directory = './' # 우분투 기준
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.conn = sqlite3.connect(self.directory+'/JMSPlant.db', check_same_thread=False)
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
        );
        """
        try:
            self.cursor.executescript(query)
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

    def smartFarm_insert_data(self, data) -> None:
        '''
        DB에 데이터 삽입
        '''
        if( data.get("sysfan") != None and      data.get("wpump") != None and
            data.get("led") != None and         data.get("humidity") != None and
            data.get("temperature") != None and data.get("ground1")!= None and
            data.get("ground2")):

            current_time = datetime.now(timezone(timedelta(hours=9)))
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            query = """
            INSERT INTO smartFarm (IsRun, sysfan, wpump, led, humidity, temperature, ground1, ground2,created_at,updated_at,deleted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """
            self.cursor.execute(query,(1,data.get("sysfan"),
                                        data.get("wpump"),
                                        data.get("led"),
                                        data.get("humidity"),
                                        data.get("temperature"),
                                        data.get("ground1"),
                                        data.get("ground2"),
                                        current_time_str,
                                        current_time_str))
            self.conn.commit()

class Ardu(device_data):
    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.port = self.ar_get("USB")
        self.arduino = None
        self.data = {"isrun": False,
                     "sysfan": False,
                     "wpump": False,
                     "led": False,
                     "humidity": 0.0,
                     "temperature": 0.0,
                     "ground1": 0,
                     "ground2": 0}
        self.last_print_time = time.time()
        try:
            self.arduino = serial.Serial(self.port, 9600)
        except Exception as e:
            print(f"Port Error: {e}")
            exit(1)
        time.sleep(2)

    def parse_data(self, data_line):
        data_handlers = {
            "isrun": lambda x: bool(int(x)),
            "d_sysfan": lambda x: bool(int(x)),
            "d_wpump": lambda x: bool(int(x)),
            "d_led": lambda x: bool(int(x)),
            "humidity": lambda x: float(x.split("%")[0]), # "%"를 기준으로 분리하고 첫 번째 요소를 float으로 변환
            "temperature": lambda x: float(x.split("*C")[0]), # "*C"를 기준으로 분리하고 첫 번째 요소를 float으로 변환
            "ground1": lambda x: round((int(x) / 1024) * 100, 1),
            "ground2": lambda x: round((int(x) / 1024) * 100, 1),
        }

        key, value = data_line.split(":")
        key = key.strip().lower() # 키를 소문자로 변환
        value = value.strip()
        if key in data_handlers: # 데이터 핸들링 함수가 있는 경우, 해당 함수로 값 처리
            handled_value = data_handlers[key](value)
            self.data[key] = handled_value
        else:
            pass

    def read_data(self) -> None:
        data = None
        if self.arduino.in_waiting > 0:
            try:
                data = self.arduino.readline().decode().rstrip()
            except:
                pass
        if not data:
            return
        self.parse_data(data)

    def update(self) -> None:
        if time.time() - self.last_print_time < 10:
            return
        # 딕셔너리의 값들을 출력
        print(" ".join(f"{k}: {v}" for k, v in self.data.items()))
        # 딕셔너리를 이용하여 데이터베이스 삽입
        self.db.smartFarm_insert_data(self.data)
        self.last_print_time = time.time()

if __name__ == "__main__":
    Ar = Ardu()
    while True:
        Ar.read_data()
        Ar.update()