"""Load test: locust -f tests/locust/locustfile.py --host https://localhost  (the CI-mode stack is the staging target)

Headless, 1000 users, ramp 50/s, 5 minutes:
  locust -f tests/locust/locustfile.py --host https://localhost --headless -u 1000 -r 50 -t 5m --csv results/run
Run once with Redis cache on and once with DASHBOARD_CACHE_SECONDS=0 to compare p95.

All simulated users come from one IP, so raise the throttles on the target first
(THROTTLE_ANON=100000/min THROTTLE_AUTH=100000/min AXES_ENABLED=0), otherwise most
logins get 429 and the test measures the rate limiter instead of the API.
"""

import random

from locust import HttpUser, between, task

USERS = ["arta", "leon", "vjosa", "blerim", "rina", "ilir", "besa", "driton"]
PASSWORD = "Demo-Pass-2026!"


class Employee(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.client.verify = False  # self-signed certificate on the local stack
        email = f"{random.choice(USERS)}@expenseflow.dev"
        r = self.client.post("/api/v1/auth/login/", json={"email": email, "password": PASSWORD}, name="login")
        self.client.headers["Authorization"] = f"Bearer {r.json().get('access', '')}"

    @task(5)
    def dashboard(self):
        self.client.get("/api/v1/reports/dashboard/", name="dashboard")

    @task(3)
    def list_expenses(self):
        self.client.get("/api/v1/expenses/?page_size=20", name="expenses list")

    @task(1)
    def search(self):
        self.client.get("/api/v1/expenses/?q=lunch", name="expenses search")
