from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User, EmailDomain


class DomainsApi(TestCase):
    def setUp(self):
        EmailDomain.objects.create(
            domain="@accepted.test", status=EmailDomain.STATUS_ACCEPTED
        )
        EmailDomain.objects.create(
            domain="@rejected.test", status=EmailDomain.STATUS_REJECTED
        )
        EmailDomain.objects.create(
            domain="@pending.test", status=EmailDomain.STATUS_PENDING
        )

    def test_accepted_domains_list(self):
        client = APIClient()
        response = client.get("/domains/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["results"], [
            {
                "domain": "@accepted.test",
                "status": "ACK"
            }
        ])
