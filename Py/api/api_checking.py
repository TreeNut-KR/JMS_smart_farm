from fastapi.testclient import TestClient
import sys
sys.path.append('.\\JMS_smart_farm\\Py\\api')
from complexed_chart import app

client = TestClient(app)

def test_read_main():
    # 요청을 보낼 주소 목록
    get_endpoints = ["/api", "/api/latest"]
    for get_point in get_endpoints:
        response = client.get(get_point)
        assert response.status_code == 200
    

    get_endpoints = ["/api/date", "/api/month"]
    for get_point in get_endpoints:
        response = client.get(get_point+"?checkdate=2024-05-16")
        assert response.status_code == 200
        
    response = client.post("/api/week", json={"year": 2024,"month": 5,"week": 2})
    assert response.status_code == 200

    # senddata POST 요청은 별도로 처리
    response_api_senddata = client.post("/api/senddata", json={"LED": True, "SYSFAN": False})
    assert response_api_senddata.status_code == 200

if __name__ == "__main__":
    test_read_main()