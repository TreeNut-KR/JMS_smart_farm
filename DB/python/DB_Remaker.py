import sqlite3
import os

# 기존 데이터베이스에 연결
conn = sqlite3.connect('DB\\20240213\\JMSPlant.db')
cursor = conn.cursor()

# NULL 값을 포함하는 행 삭제
cursor.execute("DELETE FROM ardu_data WHERE time IS NULL OR ground1 IS NULL OR ground2 IS NULL OR humidity IS NULL OR temperature IS NULL")
conn.commit()

# 새로운 데이터베이스 파일을 저장할 디렉토리 생성
new_db_directory = 'DB\\20240213\\'
os.makedirs(new_db_directory, exist_ok=True)

# 새로운 데이터베이스 파일에 변경사항 저장
backup_conn = sqlite3.connect(new_db_directory + 'JMSPlant_remake.db')
conn.backup(backup_conn)

# 연결 종료
cursor.close()
conn.close()
backup_conn.close()