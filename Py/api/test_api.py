import pytest
from httpx import AsyncClient
import sys
sys.path.append('.\\JMS_smart_farm\\Py\\api')
import complexed_chart
from complexed_chart import app

@pytest.mark.anyio
async def test_black_box():
    '''
    black box test

    get  : /api, /api/latest
    post : /api/week, /api/date, /api/month, /api/hourly
    '''
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # GET 요청 테스트
        get_endpoints = ["/api", "/api/latest"]
        for endpoint in get_endpoints:
            response = await ac.get(endpoint)
            assert response.status_code == 200

        # POST 요청 테스트
        post_endpoints = {
            "/api/date": {"date": "2024-05-16"},
            "/api/hourly": {"date": "2024-05-16"},
            "/api/week": {"year": 2024, "month": 12, "week": 2},
            "/api/month": {"year": 2024, "month": 12},
        }

        for endpoint, data in post_endpoints.items():
            response = await ac.post(endpoint, json=data)
            assert response.status_code == 200

class WhiteTest:
    def __init__(self) -> None:
        self.complexed_chart = complexed_chart
        self.complexed_chart.get_db_connection("JMSPlant_test.db")

    async def __call__(self) -> None:
        await self.test_white_week_date()
        await self.test_white_week_days()
    
    async def test_white_week_date(self) -> None:
        current_date_item = None
        data_item = self.complexed_chart.week_date(year=2024, month=3, week_index=5)
        data_bool = data_item == current_date_item
        print(
            f"{data_bool}\n"
            f"data_item         : {data_item}\n"
            f"current_date_item : {current_date_item}"
        )
        assert data_item == current_date_item

    async def test_white_week_days(self) -> None:
        # 기존 코드와 같이 로직 구현. 비동기가 필요한 경우 httpx.AsyncClient 사용 예시 적용
        pass

@pytest.mark.anyio
async def main():
    white_test_instance = WhiteTest()
    await white_test_instance()
    await test_black_box()

if __name__ == "__main__":
    pytest.main()
