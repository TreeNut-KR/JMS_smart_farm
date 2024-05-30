import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta
import sys
sys.path.append('.\\JMS_smart_farm\\API')
import complexed_chart
from complexed_chart import app

@pytest.mark.anyio
async def test_black_box():
    '''
    black box test

    get  : /api/latest, /api/idx100
    post : /api/week, /api/month, /api/hourly
    '''
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # GET 요청 테스트
        get_endpoints = ["/api/latest", "/api/idx100"]
        for endpoint in get_endpoints:
            response = await ac.get(endpoint)
            assert response.status_code == 200

        # POST 요청 테스트
        post_endpoints = {
            "/api/hourly": {"date": "2024-05-16"},
            "/api/week": {"year": 2024, "month": 12, "week": 4},
            "/api/month": {"year": 2024, "month": 12},
        }

        for endpoint, data in post_endpoints.items():
            response = await ac.post(endpoint, json=data)
            assert response.status_code == 200

class WhiteTest:
    def __init__(self) -> None:
        self.complexed_chart = complexed_chart

    async def __call__(self) -> None:
        self.test_white_week_date()
        self.test_white_week_days()
    
    def test_white_week_date(self) -> None:
        current_date_item = None
        data_item, _ = self.complexed_chart.datetime_date(year=2024, month=3, index=5)
        data_bool = data_item == current_date_item
        print(
            f"{data_bool}\n"
            f"data_item         : {data_item}\n"
            f"current_date_item : {current_date_item}"
        )
        assert data_item == current_date_item

    async def test_white_week_days(self) -> None:
        current_date=[]
        days = 31
        start_date = datetime.strptime("2024-06-30", "%Y-%m-%d") # 경계 날짜 테스트
        for i in range(days):
            current_date.append(str(start_date + timedelta(days=i)))

        date_list = [start_date + timedelta(days=i) for i in range(days)] 
        rows =  self.complexed_chart.DB_Query().fetch_weekly_data(checkdate=start_date)
        data_items = await self.complexed_chart.datetime_days(date_list, rows)    
        
        print("")
        for index, (data_item, current_date_item) in enumerate(zip(data_items, current_date)):
            data_bool = data_item['created_at'] == current_date_item
            print(
                f"{index, data_bool}\n"
                f"data_item['created_at'] : {data_item['created_at']}\n"
                f"current_date_item       : {current_date_item}"
                )
            assert data_item['created_at'] == current_date_item

@pytest.mark.anyio
async def main():
    await test_black_box()

if __name__ == "__main__":
    white_test_instance = WhiteTest()
    asyncio.run(white_test_instance())
    pytest.main()