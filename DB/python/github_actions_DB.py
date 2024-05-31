import sqlite3
from sqlite3 import Error
from pathlib import Path
import os

class DatabaseManager:
    def __init__(self, db_name='JMSPlant_test.db'):
        self.db_path = Path("./").joinpath(db_name).resolve()

    def create_connection(self):
        """데이터베이스 연결 생성 및 반환"""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except Error as e:
            print(e)
        return None

    def create_tables(self, conn):
        """데이터베이스 테이블 생성"""
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
        self.execute_query(conn, smart_farm_table_query)

    def insert_sample_data(self, conn):
        """샘플 데이터 추가"""
        sample_data_query = """
        BEGIN;

        WITH RECURSIVE dates(date) AS (
            SELECT '2024-05-15 00:00:00'
            UNION ALL
            SELECT datetime(date, '+60 seconds')
            FROM dates
            WHERE date < '2024-06-15 00:00:00'
        )
        INSERT INTO smartFarm (IsRun, sysfan, wpump, led, humidity, temperature, ground1, ground2, created_at)
        SELECT
            0 AS IsRun,
            1 AS sysfan,
            abs(random()) % 2 AS wpump,
            1 AS led,
            50 + abs(random()) % 21 AS humidity,
            20 + abs(random()) % 9 AS temperature,
            40 + abs(random()) % 41 AS ground1,
            40 + abs(random()) % 41 AS ground2,
            date AS created_at
        FROM dates;

        COMMIT;
        """
        self.execute_query(conn, sample_data_query)

    def execute_query(self, conn, query):
        """데이터베이스에 쿼리 실행"""
        try:
            cursor = conn.cursor()
            cursor.executescript(query)
        except Error as e:
            print(e)

    def __call__(self):
        """클래스 인스턴스 호출 시 데이터베이스 연결, 테이블 생성, 샘플 데이터 추가"""
        with self.create_connection() as conn:
            if conn is not None:
                self.create_tables(conn)
                self.insert_sample_data(conn)
            else:
                print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    db_manager = DatabaseManager()
    db_manager()
