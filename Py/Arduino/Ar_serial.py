from datetime import datetime, timezone, timedelta
import time
import pytz
import platform
import serial
import serial.tools.list_ports
import sqlite3

class Database:
    def __init__(self):
        self.DATABASE = 'JMSPlant.db'

    def smartFarm_insert_data(self, checkdata) -> None:
        '''DB에 데이터 삽입'''
        required_keys = ["sysfan", "wpump", "led", "humidity", "temperature", "ground1", "ground2", "created_at", "updated_at",]
        if all(checkdata.get(key) is not None for key in required_keys):
            query = """
            INSERT INTO smartFarm (IsRun, sysfan, wpump, led, humidity, temperature, ground1, ground2, created_at, updated_at, deleted_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """
            query_data = (
                checkdata.get("sysfan"),
                checkdata.get("wpump"),
                checkdata.get("led"),
                checkdata.get("humidity"),
                checkdata.get("temperature"),
                checkdata.get("ground1"),
                checkdata.get("ground2"),
                checkdata.get("created_at"),
                checkdata.get("updated_at"))
            
            with sqlite3.connect(self.DATABASE) as db:
                db.execute(query, query_data)
                db.commit()

class Ardu:
    def __init__(self) -> None:
        self.db = Database()
        self.port = self.find_arduino_port()
        self.arduino = self.connect_to_arduino()
        self.initialize_data()

    def find_arduino_port(self):
        os_type = platform.system()
        if os_type == "Windows":
            mod = "CH340"  # 윈도우의 경우
        else:
            mod = "USB" # 리눅스 기반의 경우
        ports = serial.tools.list_ports.comports()
        for port_get in sorted(ports):
            if mod in port_get.description:
                print(f"Found Arduino on {port_get.device} ({os_type})")
                return port_get.device
        print("Arduino not found")
        return None

    def connect_to_arduino(self):
        if self.port is None:
            print("No port found for Arduino")
            exit(1)
        try:
            arduino = serial.Serial(self.port, 9600)
            time.sleep(2)  # 연결 대기
            return arduino
        except Exception as e:
            print(f"Port Error: {e}")
            exit(1)

    def initialize_data(self):
        # 현재 시간을 서울 시간대로 설정
        date = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
        self.data = {
            "isrun": False,
            "sysfan": False,
            "wpump": False,
            "led": False,
            "humidity": 0.0,
            "temperature": 0.0,
            "ground1": 0,
            "ground2": 0,
            "created_at": date,
            "updated_at": date
        }

    def parse_data(self, data_line, current_time):
        # 쉼표로 데이터를 구분한 후 각 항목을 처리
        data_items = data_line.split(", ")
        data_handlers = {
            "isrun": lambda x: bool(int(x)),
            "sysfan": lambda x: bool(int(x)),
            "wpump": lambda x: bool(int(x)),
            "led": lambda x: bool(int(x)),
            "humidity": lambda x: float(x.split("%")[0]), # "%"를 기준으로 분리하고 첫 번째 요소를 float으로 변환
            "temperature": lambda x: float(x.split("*C")[0]), # "*C"를 기준으로 분리하고 첫 번째 요소를 float으로 변환
            "ground1": lambda x: int(x),
            "ground2": lambda x: int(x)
        }

        for item in data_items:
            key, value = item.split(":")
            key = key.strip().lower().replace(" ", "") # 키를 소문자로 변환하고 공백 제거
            value = value.strip()
            if key in data_handlers: # 데이터 핸들링 함수가 있는 경우, 해당 함수로 값 처리
                handled_value = data_handlers[key](value)
                self.data[key] = handled_value
                self.data["created_at"] = current_time
                self.data["updated_at"] = current_time
                
    def update(self) -> None:
        print(" ".join(f"{k}: {v}" for k, v in self.data.items()))
        self.db.smartFarm_insert_data(self.data)

if __name__ == "__main__":
    ardu = Ardu()  # Ardu 인스턴스 생성
    Time_seoul = datetime.now(pytz.timezone('Asia/Seoul'))  # 초기 값 설정, 첫 반복에서 조건을 만족시키기 위함
    while True:
        current_time = datetime.now(pytz.timezone('Asia/Seoul'))
        elapsed_time = (current_time - Time_seoul).total_seconds()
        if elapsed_time < 10:
            time.sleep(1)  # 1초 동안 일시 중지합니다.
            continue
        try:
            ardu.arduino.write(b'1')  # 아두이노로 신호를 보냄
            data = ardu.arduino.readline().decode().rstrip()
            ardu.parse_data(data, current_time.strftime('%Y-%m-%d %H:%M:%S'))  # 데이터 처리
            ardu.update()
            Time_seoul = current_time  # 마지막 출력 시간 업데이트
        except Exception as e:
            time.sleep(1)  # 예외 발생 시에도 1초 동안 일시 중지합니다.
            continue
