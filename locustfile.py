from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_health(self):
        self.client.get("/health")

    @task(2)
    def get_users(self):
        self.client.get("/api/users")