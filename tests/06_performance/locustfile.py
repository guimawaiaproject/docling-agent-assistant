"""
Load testing — simulation utilisateurs réels.
Lancer : locust -f tests/06_performance/locustfile.py --host=http://localhost:8000
"""

import uuid

from faker import Faker
from locust import HttpUser, between, task

fake = Faker("fr_FR")


class DoclingUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        self.email = f"load_{uuid.uuid4().hex[:8]}@test.com"
        self.password = f"Load@{uuid.uuid4().hex[:6]}!1"
        self.client.post(
            "/api/v1/auth/register",
            data={"email": self.email, "password": self.password, "name": fake.first_name()},
        )
        resp = self.client.post(
            "/api/v1/auth/login",
            data={"email": self.email, "password": self.password},
        )
        if resp.status_code == 200:
            self.token = resp.json().get("token")
            self.client.headers["Authorization"] = f"Bearer {self.token}"

    @task(5)
    def catalogue_list(self):
        self.client.get("/api/v1/catalogue?limit=20", name="/api/v1/catalogue [list]")

    @task(3)
    def stats(self):
        self.client.get("/api/v1/stats", name="/api/v1/stats")

    @task(2)
    def fournisseurs(self):
        self.client.get("/api/v1/catalogue/fournisseurs", name="/api/v1/catalogue/fournisseurs")

    @task(1)
    def batch_save(self):
        products = [
            {
                "fournisseur": f"Load_{uuid.uuid4().hex[:6]}",
                "designation_raw": fake.catch_phrase()[:80],
                "designation_fr": fake.catch_phrase()[:80],
                "famille": "Autre",
                "prix_brut_ht": 10.0,
                "prix_remise_ht": 10.0,
                "prix_ttc_iva21": 12.1,
                "confidence": "high",
            },
        ]
        self.client.post(
            "/api/v1/catalogue/batch",
            json={"produits": products, "source": "pc"},
            name="/api/v1/catalogue/batch [create]",
        )
