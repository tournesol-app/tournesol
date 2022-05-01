from django.test import TestCase
from rest_framework.test import APIClient


class ApiI18n(TestCase):
    def test_default_language_english(self):
        client = APIClient()
        response = client.post(
            "/accounts/register/",
            data={
                "email": "test",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data["password"], ["This field is required."])
        self.assertEqual(response_data["email"], ["Enter a valid email address."])

    def test_set_language_in_headers(self):
        client = APIClient(HTTP_ACCEPT_LANGUAGE="fr")
        response = client.post(
            "/accounts/register/",
            data={
                "email": "test",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data["password"], ["Ce champ est obligatoire."])
        self.assertEqual(
            response_data["email"], ["Saisissez une adresse e-mail valide."]
        )
