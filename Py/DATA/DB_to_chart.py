import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class chart:
    def __init__(self) -> None:
        # 데이터베이스 연결
        self.conn = sqlite3.connect('DB\\20240213\\JMSPlant_remake.db')
        self.cursor = self.conn.cursor()

    def get_columns(self, column_type):
        # 모든 컬럼의 정보 가져오기
        self.cursor.execute("PRAGMA table_info(ardu_data)")
        columns_info = self.cursor.fetchall()

        # column_type에 맞는 컬럼만 선택
        valid_columns = [column[1] for column in columns_info if column[2] == column_type and column[1] != 'id']

        return valid_columns

    def draw(self, column_type, subplot) -> None:
        valid_columns = self.get_columns(column_type)

        for column in valid_columns:
            # 쿼리 실행
            query = f"SELECT time, {column} FROM ardu_data WHERE {column} IS NOT NULL"
            self.cursor.execute(query)

            # 결과 가져오기
            results = self.cursor.fetchall()

            # 데이터 추출
            x = [mdates.datestr2num(row[0]) for row in results]  # 시간컬럼
            y = [row[1] for row in results]  # 선택한 컬럼

            # 그래프 그리기
            subplot.plot_date(x, y, label=column, linestyle='solid', marker='None')

        # 그래프 레이블과 타이틀 설정
        subplot.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        subplot.xaxis.set_major_locator(mdates.AutoDateLocator())
        subplot.set_xlabel('time')
        subplot.legend()  # 범례 표시
        subplot.set_title(f'{column_type} DATA CHART')

    def close(self):
        # 연결 종료
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":
    # 그래프 생성
    fig, axs = plt.subplots(2)

    # 데이터베이스 연결 및 그래프 생성
    DB = chart()
    DB.draw('REAL', axs[0])
    DB.draw('INTEGER', axs[1])

    # 연결 종료
    DB.close()

    # 그래프 표시
    plt.tight_layout()
    plt.show()
