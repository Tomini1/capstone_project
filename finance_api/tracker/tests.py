from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class FinanceAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="abi", email="abi@example.com", password="pass12345")

    def auth(self):
        # Djoser token login
        res = self.client.post("/auth/token/login/", {"username": "abi", "password": "pass12345"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        token = res.data["auth_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_user_register_and_retrieve(self):
        res = self.client.post("/api/users/", {"username": "newuser", "email": "n@e.com", "password": "secret123"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Login as new user and retrieve own profile
        res_login = self.client.post("/auth/token/login/", {"username": "newuser", "password": "secret123"})
        self.assertEqual(res_login.status_code, status.HTTP_200_OK)
        token = res_login.data["auth_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        res_me = self.client.get(f"/api/users/{res.data['id']}/")
        self.assertEqual(res_me.status_code, status.HTTP_200_OK)

    def test_category_transaction_and_reports(self):
        self.auth()
        # Create category
        res_cat = self.client.post("/api/categories/", {"name": "Food"}, format="json")
        self.assertEqual(res_cat.status_code, status.HTTP_201_CREATED)
        cat_id = res_cat.data["id"]

        # Create income
        res_inc = self.client.post("/api/transactions/", {
            "category": cat_id, "amount": "250000.00", "type": "INCOME", "description": "Salary", "date": "2025-08-01"
        }, format="json")
        self.assertEqual(res_inc.status_code, status.HTTP_201_CREATED)

        # Create expense
        res_exp = self.client.post("/api/transactions/", {
            "category": cat_id, "amount": "15000.50", "type": "EXPENSE", "description": "Groceries", "date": "2025-08-02"
        }, format="json")
        self.assertEqual(res_exp.status_code, status.HTTP_201_CREATED)

        # Monthly summary
        res_sum = self.client.get("/api/reports/monthly-summary/?month=08&year=2025")
        self.assertEqual(res_sum.status_code, status.HTTP_200_OK)
        self.assertEqual(res_sum.data["income"], "250000")
        self.assertEqual(res_sum.data["expense"], "15000.5")

        # Category breakdown
        res_cb = self.client.get("/api/reports/category-breakdown/?month=08&year=2025")
        self.assertEqual(res_cb.status_code, status.HTTP_200_OK)
        self.assertTrue(any(i["category"] == "Food" for i in res_cb.data["items"]))
