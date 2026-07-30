"""Tests of the auth_app: registration, login and email check."""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class RegistrationTests(APITestCase):
    """Tests the registration endpoint."""

    def setUp(self):
        self.url = reverse("registration")
        self.payload = {
            "fullname": "Max Mustermann",
            "email": "max@test.de",
            "password": "geheim123",
            "repeated_password": "geheim123",
        }

    def test_registration_success(self):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["email"], "max@test.de")
        self.assertEqual(response.data["fullname"], "Max Mustermann")

    def test_registration_password_mismatch(self):
        self.payload["repeated_password"] = "anders"
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_email(self):
        self.client.post(self.url, self.payload)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_single_name(self):
        self.payload["fullname"] = "Cher"
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginTests(APITestCase):
    """Tests the login endpoint."""

    def setUp(self):
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="max@test.de", email="max@test.de", password="geheim123"
        )

    def test_login_success(self):
        response = self.client.post(
            self.url, {"email": "max@test.de", "password": "geheim123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            self.url, {"email": "max@test.de", "password": "falsch"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailCheckTests(APITestCase):
    """Tests the email check endpoint."""

    def setUp(self):
        self.url = reverse("email-check")
        self.user = User.objects.create_user(
            username="max@test.de", email="max@test.de",
            password="geheim123", first_name="Max", last_name="Mustermann",
        )
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_email_check_found(self):
        response = self.client.get(self.url, {"email": "max@test.de"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["fullname"], "Max Mustermann")

    def test_email_check_not_found(self):
        response = self.client.get(self.url, {"email": "gibtsnicht@test.de"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_email_check_missing_param(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_check_requires_auth(self):
        self.client.credentials()
        response = self.client.get(self.url, {"email": "max@test.de"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
