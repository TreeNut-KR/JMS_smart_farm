from pathlib import Path
import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name='JMSPlant.db'):
        script_dir = Path("./").resolve()
        self.db_path = os.path.join(script_dir, db_name)

    def __call__(self):
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            self.create_tables(conn)
            self.insert_sample_data(conn)  # 샘플 데이터 추가 메소드 호출

    def create_tables(self, conn):
        smart_farm_table_query = """
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
        user_info_table_query = """
        CREATE TABLE IF NOT EXISTS user_info (
            id TEXT PRIMARY KEY,
            email TEXT,
            verified_email BOOL,
            name TEXT,
            given_name TEXT,
            family_name TEXT,
            picture TEXT,
            locale TEXT
        );
        """
        cursor = conn.cursor()
        # Executes multiple SQL commands at once
        cursor.executescript(smart_farm_table_query + user_info_table_query)
        # commit() is not needed here as it's automatically called by the context manager

    def insert_sample_data(self, conn):
        # smartFarm 테이블에 샘플 데이터 추가
        insert_query = """
        INSERT INTO smartFarm (IsRun, sysfan, wpump, led, humidity, temperature, ground1, ground2)
        VALUES (1, 1, 1, 1, 50.5, 22.5, 500, 500);
        """
        cursor = conn.cursor()
        cursor.execute(insert_query)
        # 여기서도 commit() 호출이 필요 없음. with 문(context manager)이 자동으로 처리함.

DB_setup = DatabaseManager()
DB_setup()
