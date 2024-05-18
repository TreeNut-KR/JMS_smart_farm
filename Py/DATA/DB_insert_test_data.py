import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('./JMSPlant.db') # 상대 경로에 데이터베이스 연결 생성
        return conn
    except Error as e:
        print(e)

    return conn

def execute_query(conn, query): 
    try:
        cursor = conn.cursor()
        cursor.executescript(query)
    except Error as e:
        print(e)

def main():
    conn = create_connection()

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

    INSERT INTO ArduinoControl (led, sysfan, updated_at) VALUES (1, 0, CURRENT_TIMESTAMP);

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
        50 + abs(random()) % 21 AS humidity, -- 50에서 70 사이의 값
        20 + abs(random()) % 9 AS temperature, -- 20에서 28 사이의 값
        40 + abs(random()) % 41 AS ground1, -- 40에서 80 사이의 값
        40 + abs(random()) % 41 AS ground2, -- 40에서 80 사이의 값
        date AS created_at
    FROM dates;

    COMMIT;
    """

    if conn is not None:
        execute_query(conn, query)
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
