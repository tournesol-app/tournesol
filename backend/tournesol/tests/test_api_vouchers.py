from django.db.models import ObjectDoesNotExist
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from vouch.models import Voucher


class VoucherCreateApi(TestCase):
    """
    TestCase of the voucher creation API.
    """

    def setUp(self):
        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")

        self.valid_create_params = {
            "to": "user2",
            "is_public": False,
            "value": "1",
        }

    def test_anonymous_cant_create(self):
        """
        An anonymous user can't create a voucher.
        """
        client = APIClient()

        initial_voucher_count = Voucher.objects.all().count()
        response = client.post("/vouchers/", self.valid_create_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)

    def test_create_voucher(self):
        """
        A user can create a voucher.
        """
        client = APIClient()
        client.force_authenticate(user=self.user1)

        initial_voucher_count = Voucher.objects.all().count()
        response = client.post("/vouchers/", self.valid_create_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count + 1)

        new_voucher = Voucher.objects.get(by=self.user1.id, to=self.user2.id)
        self.assertEqual(new_voucher.is_public, self.valid_create_params["is_public"])
        self.assertEqual(new_voucher.value, float(self.valid_create_params["value"]))

    def test_cannot_create_to_inexistant_user(self):
        """
        A user can't create a voucher to an inexistant user.
        """
        client = APIClient()
        client.force_authenticate(user=self.user1)

        initial_voucher_count = Voucher.objects.all().count()
        params = self.valid_create_params | {"to": "inexistant"}
        response = client.post("/vouchers/", params, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)

    def test_cannot_create_twice_to_the_same_user(self):
        """
        The same voucher cannot be created twice with the same `to`.
        """
        client = APIClient()
        client.force_authenticate(user=self.user1)

        response = client.post("/vouchers/", self.valid_create_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        initial_voucher_count = Voucher.objects.all().count()
        response = client.post("/vouchers/", self.valid_create_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)

    def test_cannot_create_voucher_to_oneself(self):
        """
        A user cannot vouch for themself.
        """
        user = self.user1

        client = APIClient()
        client.force_authenticate(user=user)

        initial_voucher_count = Voucher.objects.all().count()
        params = self.valid_create_params | {"to": "user1"}
        response = client.post("/vouchers/", params, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)
        self.assertEqual(response.content, b'{"to":["You cannot vouch for yourself"]}')


class VoucherDeleteApi(TestCase):
    """
    TestCase of the voucher delete API.
    """

    def setUp(self):
        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")

        self.voucher = Voucher.objects.create(by=self.user1, to=self.user2, value=1)

    def test_anonymous_cant_delete(self):
        """
        An anonymous user can't delete a voucher.
        """
        client = APIClient()

        initial_voucher_count = Voucher.objects.all().count()
        response = client.delete("/vouchers/{}/".format(self.voucher.pk), format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)

    def test_user_can_delete(self):
        """
        A user can delete their voucher.
        """
        client = APIClient()

        client.force_authenticate(user=self.user1)
        response = client.delete("/vouchers/{}/".format(self.voucher.pk), format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            Voucher.objects.get(pk=self.voucher.pk)

    def test_user_cant_delete_other_users_vouchers(self):
        """
        A user can't delete another user's voucher.
        """
        client = APIClient()
        client.force_authenticate(user=self.user2)

        response = client.delete("/vouchers/{}/".format(self.voucher.pk), format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        Voucher.objects.get(pk=self.voucher.pk)
