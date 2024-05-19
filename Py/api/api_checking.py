from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
sys.path.append('.\\JMS_smart_farm\\Py\\api')
import complexed_chart
from complexed_chart import app

client = TestClient(app)

def black_test_instance() -> None:
    '''
    black box test

    get  : /api, /api/latest
    post : /api/week, /api/date, /api/month,/api/hourly
    '''
    
    # 요청을 보낼 주소 목록
    get_endpoints = ["/api", "/api/latest"]
    for get_point in get_endpoints:
        response = client.get(get_point)
        assert response.status_code == 200

    post_endpoints = ["/api/date", "/api/hourly"]
    for post_endpoint in post_endpoints:
        response = client.post(post_endpoint, json={"date": "2024-05-16"})
        assert response.status_code == 200

    response = client.post("/api/week", json={"year": 2024,"month": 12,"week": 2})
    assert response.status_code == 200

    response = client.post("/api/month", json={"year": 2024,"month": 12})
    assert response.status_code == 200

class white_test():
    def __init__(self) -> None:
        self.complexed_chart = complexed_chart
        self.complexed_chart.get_db_connection("JMSPlant_test.db")

    def __call__(self) -> None:
        self.test_white_week_date()
        self.test_white_week_days()
    
    def test_white_week_date(self) -> None:
        current_date_item = None # 24.03 5주차 X, 24.04 1주차 O => None
        data_item = self.complexed_chart.week_date(year=2024,
                                                    month=3,
                                                    week_index=5) # 주간 인덱스가 5인 경우
        data_bool = data_item == current_date_item
        print(
            f"{data_bool}\n"
            f"data_item         : {data_item}\n"
            f"current_date_item : {current_date_item}"    
            )
        assert data_item == current_date_item

    def test_white_week_days(self) -> None:
        current_date_item = None  
        days = 32 # 경계 데이터 테스트
        start_date = datetime.strptime("2024-05-01", "%Y-%m-%d")
        data_item = self.complexed_chart.week_days(start_date,
                                                   days=days,
                                                   control=3) # 1주일 컬럼문(3)인 경우
        data_bool = data_item == current_date_item
        print(
            f"{data_bool}\n"
            f"data_item         : {data_item}\n"
            f"current_date_item : {current_date_item}"    
            )
        assert data_item == current_date_item

        current_date=[]
        days = 31
        start_date = datetime.strptime("2024-06-30", "%Y-%m-%d") # 경계 날짜 테스트 
        for i in range(days):
            current_date.append(str(start_date + timedelta(days=i)))
        data_items = self.complexed_chart.week_days(start_date,
                                                    days=days,
                                                    control=3)
        print("")
        for index, (data_item, current_date_item) in enumerate(zip(data_items, current_date)):
            data_bool = data_item['created_at'] == current_date_item
            print(
                f"{index, data_bool}\n"
                f"data_item['created_at'] : {data_item['created_at']}\n"
                f"current_date_item       : {current_date_item}"    
                )
            assert data_item['created_at'] == current_date_item

if __name__ == "__main__":
    white_test_instance = white_test()
    white_test_instance()
    black_test_instance()
    