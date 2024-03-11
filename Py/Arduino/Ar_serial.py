import serial.tools.list_ports
from datetime import datetime, timezone, timedelta
import time
import os
import sqlite3

from USB_device import Usb

class Database:
    def __init__(self):
        self.directory = 'C:/JMS'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.conn = sqlite3.connect(self.directory + '/JMSPlant.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS smartFarm (
            idx INTEGER PRIMARY KEY AUTOINCREMENT,
            IsRun BOOL,
            sysfan BOOL,
            wpump BOOL,
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

    def insert_data(self, IsRun, sysfan, wpump, humidity, temperature, ground1, ground2):
        current_time = datetime.now(timezone(timedelta(hours=9)))
        current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
        query = """
        INSERT INTO smartFarm ( IsRun, sysfan, wpump, humidity, temperature, ground1, ground2,created_at,updated_at,deleted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,NULL)
        """
        self.cursor.execute(query, (current_time_str, IsRun, sysfan, wpump, humidity, temperature, ground1, ground2,current_time_str, current_time_str))
        self.conn.commit()

class Ardu(Usb):
    def __init__(self) -> None:
        super().__init__()
        self.db = Database()

        self.port = self.usb_get("CH340")
        self.arduino = None
        self.defl = "0"

        self.IsRun = None
        self.sysfan = None
        self.wpump = None
        self.humidity = None
        self.temperature = None
        self.ground1 = None
        self.ground2 = None
        self.a =1
        self.last_print_time = time.time()

        try:
            self.arduino = serial.Serial(self.port, 9600)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(2)

    def read_serial_data(self):
        if self.arduino.in_waiting > 0:
            data = self.arduino.readline().decode().rstrip()
            return data


    def send_data(self, data):
        self.arduino.write(('Serial.println('+data+')').encode())
        print("Sneding_Test : " + data)
        time.sleep(2)


    def read_data(self):
        data = self.read_serial_data()
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
                print(f"Received data - \nIsRun: {self.IsRun}, SYSFAN: {self.sysfan}, WPUMP: {self.wpump}, Humidity: {self.humidity}%, Temperature: {self.temperature}°C, Ground1: {self.ground1}, Ground2: {self.ground2}")
                self.db.insert_data(self.IsRun, self.sysfan, self.wpump, self.humidity, self.temperature, self.ground1, self.ground2)
                self.last_print_time = time.time()  # Update the last print time


if __name__ == "__main__":
    ardu_instance = Ardu()
    #ardu_instance.read_data()
    test = "TEST"
    while 1:
        ardu_instance.read_data()
        ardu_instance.send_data(test)