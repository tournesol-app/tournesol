from django.db.models import ObjectDoesNotExist
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from vouch.models import Voucher


class VoucherCreateAPIViewTestCase(TestCase):
    """
    TestCase of the `VoucherCreateAPIView` API.
    """

    def setUp(self):
        self.client = APIClient()
        self.voucher_base_url = "/users/me/vouchers/"

        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")

        self.valid_create_params = {
            "to": "user2",
        }

    def test_anon_401_create(self):
        """
        An anonymous user cannot create a voucher.
        """
        initial_voucher_count = Voucher.objects.all().count()
        response = self.client.post(
            self.voucher_base_url, self.valid_create_params, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)

    def test_auth_201_create(self):
        """
        An authenticated user can create a voucher.
        """
        self.client.force_authenticate(user=self.user1)

        initial_voucher_count = Voucher.objects.all().count()
        response = self.client.post(
            self.voucher_base_url, self.valid_create_params, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count + 1)

        new_voucher = Voucher.objects.get(by=self.user1.id, to=self.user2.id)
        self.assertEqual(new_voucher.is_public, True)
        self.assertEqual(new_voucher.value, 1.0)

        self.assertDictEqual(
            response.data,
            {
                "by": "user1",
                "to": "user2",
            },
            response.data,
        )

    def test_auth_400_create_invalid_target(self):
        """
        An authenticated user cannot give a voucher to a non-existing user.
        """
        self.client.force_authenticate(user=self.user1)

        initial_voucher_count = Voucher.objects.all().count()
        params = self.valid_create_params | {"to": "inexistant"}
        response = self.client.post(self.voucher_base_url, params, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)

    def test_auth_400_create_twice_same_target(self):
        """
        An authenticated user cannot give two vouchers to the same user.
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            self.voucher_base_url, self.valid_create_params, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        initial_voucher_count = Voucher.objects.all().count()
        response = self.client.post(
            self.voucher_base_url, self.valid_create_params, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)
        self.assertEqual(
            response.data,
            {"non_field_errors": ["You have already vouched for this user."]},
        )

    def test_auth_400_create_by_and_to_are_similar(self):
        """
        An authenticated user cannot give a voucher to him/herself.
        """
        self.client.force_authenticate(user=self.user1)

        initial_voucher_count = Voucher.objects.all().count()
        params = self.valid_create_params | {"to": "user1"}
        response = self.client.post(self.voucher_base_url, params, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)
        self.assertEqual(response.data, {"to": ["You cannot vouch for yourself."]})


class VoucherGivenDestroyAPIViewTestCase(TestCase):
    """
    TestCase of the `VoucherGivenDestroyAPIView` API.
    """

    def setUp(self):
        self.client = APIClient()
        self.voucher_base_url = "/users/me/vouchers/given/"

        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")

        self.voucher = Voucher.objects.create(by=self.user1, to=self.user2, value=1)

    def test_anon_401_delete(self):
        """
        An anonymous user cannot delete a voucher.
        """
        initial_voucher_count = Voucher.objects.all().count()
        response = self.client.delete(
            f"{self.voucher_base_url}{self.user2.username}/", format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)

    def test_auth_204_delete(self):
        """
        An authenticated user can delete any of its given vouchers.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(
            f"{self.voucher_base_url}{self.user2.username}/", format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            Voucher.objects.get(pk=self.voucher.pk)

    def test_auth_404_delete_invalid_user(self):
        """
        An authenticated user cannot delete a voucher given by a non-existing
        user.
        """
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f"{self.voucher_base_url}unknown/", format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        Voucher.objects.get(pk=self.voucher.pk)

    def test_auth_404_delete_someone_else_voucher(self):
        """
        An authenticated user cannot delete a voucher given by another user,
        even if he is the receiver.
        """
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(
            f"{self.voucher_base_url}{self.user2.username}/", format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        Voucher.objects.get(pk=self.voucher.pk)


class VoucherGivenListAPIViewTestCase(TestCase):
    """
    TestCase of the `VoucherGivenListAPIView` API.
    """

    def setUp(self):
        self.client = APIClient()

        self.voucher_base_url = "/users/me/vouchers/given/"
        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")
        self.user3 = User.objects.create(username="user3", email="user3@example.com")

        self.voucher1 = Voucher.objects.create(by=self.user1, to=self.user2, value=1)
        self.voucher2 = Voucher.objects.create(
            by=self.user1,
            to=self.user3,
            value=2,
            is_public=True,
        )
        self.voucher3 = Voucher.objects.create(
            by=self.user2,
            to=self.user3,
            value=3,
        )

    def test_anon_401_list(self):
        """
        An anonymous user cannot list its given vouchers.
        """
        response = self.client.get(self.voucher_base_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_200_list(self):
        """
        An authenticated user can list its given vouchers.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.voucher_base_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        self.assertEqual(len(results), 2)

        self.assertDictEqual(
            results[0],
            {
                "by": "user1",
                "to": "user2",
            },
            results[0],
        )

        self.assertDictEqual(
            results[1],
            {
                "by": "user1",
                "to": "user3",
            },
            results[1],
        )


class VoucherReceivedListAPIViewTestCase(TestCase):
    """
    TestCase of the `VoucherReceivedListAPIView` API.
    """

    def setUp(self):
        self.client = APIClient()

        self.voucher_base_url = "/users/me/vouchers/received/"
        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")
        self.user3 = User.objects.create(username="user3", email="user3@example.com")

        self.voucher1 = Voucher.objects.create(by=self.user1, to=self.user2, value=1)
        self.voucher2 = Voucher.objects.create(
            by=self.user1,
            to=self.user3,
            value=2,
            is_public=True,
        )
        self.voucher3 = Voucher.objects.create(
            by=self.user2,
            to=self.user3,
            value=3,
        )

    def test_anon_401_list(self):
        """
        An anonymous user cannot list its received vouchers.
        """
        response = self.client.get(self.voucher_base_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_200_list(self):
        """
        An authenticated user can list its received vouchers.
        """
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.voucher_base_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        self.assertEqual(len(results), 2)

        self.assertDictEqual(
            results[0],
            {
                "by": "user1",
                "to": "user3",
            },
            results[0],
        )

        self.assertDictEqual(
            results[1],
            {
                "by": "user2",
                "to": "user3",
            },
            results[1],
        )
