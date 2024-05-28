from locust import HttpUser, task, between

class UserBehavior(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(60, 1200)

    @task
    def get_latest_data(self):
        self.client.get("/api/latest")

    @task
    def get_idx100_data(self):
        self.client.get("/api/idx100")

    @task
    def post_hourly_data(self):
        self.client.post("/api/hourly", json={"date": "2024-04-01"})

    @task
    def post_week_data(self):
        self.client.post("/api/week", json={"year": 2024, "month": 4, "week": 1})

    @task
    def post_month_data(self):
        self.client.post("/api/month", json={"year": 2024, "month": 4})
