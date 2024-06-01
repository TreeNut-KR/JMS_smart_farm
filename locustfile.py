from locust import HttpUser, task, between
import socket

def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Google의 메인 DNS 서버 주소를 사용해도 실제로 연결되지는 않지만, IP를 얻는 데 사용할 수 있습니다.
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
    finally:
        s.close()
    return IP

class UserBehavior(HttpUser):
    host = f"http://{get_host_ip()}:8000"
    wait_time = between(60, 1200)

    @task
    def get_latest_data(self):
        self.client.get("/api/latest")

    # @task
    # def get_idx100_data(self):
    #     self.client.get("/api/idx100")

    # @task
    # def post_hourly_data(self):
    #     self.client.post("/api/hourly", json={"date": "2024-04-01"})

    # @task
    # def post_week_data(self):
    #     self.client.post("/api/week", json={"year": 2024, "month": 4, "week": 1})

    # @task
    # def post_month_data(self):
    #     self.client.post("/api/month", json={"year": 2024, "month": 4})
