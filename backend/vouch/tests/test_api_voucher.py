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

        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")

        self.valid_create_params = {
            "to": "user2",
            "is_public": False,
            "value": "1",
        }

    def test_anon_401_create(self):
        """
        An anonymous user cannot create a voucher.
        """
        initial_voucher_count = Voucher.objects.all().count()
        response = self.client.post("/vouchers/", self.valid_create_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)

    def test_auth_201_create(self):
        """
        An authenticated user can create a voucher.
        """
        self.client.force_authenticate(user=self.user1)

        initial_voucher_count = Voucher.objects.all().count()
        response = self.client.post("/vouchers/", self.valid_create_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count + 1)

        new_voucher = Voucher.objects.get(by=self.user1.id, to=self.user2.id)
        self.assertEqual(new_voucher.is_public, self.valid_create_params["is_public"])
        self.assertEqual(new_voucher.value, float(self.valid_create_params["value"]))

        self.assertDictEqual(
            response.data,
            {
                "id": new_voucher.id,
                "to": "user2",
                "is_public": False,
                "value": 1,
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
        response = self.client.post("/vouchers/", params, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)

    def test_auth_400_create_twice_same_target(self):
        """
        An authenticated user cannot give two vouchers to the same user.
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.post("/vouchers/", self.valid_create_params, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        initial_voucher_count = Voucher.objects.all().count()
        response = self.client.post("/vouchers/", self.valid_create_params, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)

    def test_auth_400_create_by_and_to_are_similar(self):
        """
        An authenticated user cannot give a voucher to him/herself.
        """
        self.client.force_authenticate(user=self.user1)

        initial_voucher_count = Voucher.objects.all().count()
        params = self.valid_create_params | {"to": "user1"}
        response = self.client.post("/vouchers/", params, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Voucher.objects.all().count(), initial_voucher_count)
        self.assertEqual(response.content, b'{"to":["You cannot vouch for yourself"]}')


class VoucherDestroyAPIViewTestCase(TestCase):
    """
    TestCase of the `VoucherDestroyAPIView` API.
    """

    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")

        self.voucher = Voucher.objects.create(by=self.user1, to=self.user2, value=1)

    def test_anonymous_cant_delete(self):
        """
        An anonymous user can't delete a voucher.
        """
        initial_voucher_count = Voucher.objects.all().count()
        response = self.client.delete("/vouchers/{}/".format(self.voucher.pk), format="json")

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


class VoucherListGivenApi(TestCase):
    """
    TestCase of the voucher API to list given vouchers.
    """

    def setUp(self):
        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")
        self.user3 = User.objects.create(username="user3", email="user3@example.com")

        self.voucher1 = Voucher.objects.create(
            by=self.user1,
            to=self.user2,
            value=1
        )
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

    def test_anonymous_cannot_list(self):
        """
        An anonymous user can't list given vouchers.
        """
        client = APIClient()

        response = client.get("/vouchers/given/", format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_list(self):
        """
        A user can list their given vouchers.
        """
        client = APIClient()
        client.force_authenticate(user=self.user1)

        response = client.get("/vouchers/given/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        self.assertEqual(len(results), 2)

        self.assertDictEqual(
            results[0],
            {
                "id": self.voucher1.id,
                "to": "user2",
                "is_public": False,
                "value": 1,
            },
            results[0],
        )

        self.assertDictEqual(
            results[1],
            {
                "id": self.voucher2.id,
                "to": "user3",
                "is_public": True,
                "value": 2,
            },
            results[1],
        )


class VoucherListReceivedApi(TestCase):
    """
    TestCase of the voucher API to list received vouchers.
    """

    def setUp(self):
        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")
        self.user3 = User.objects.create(username="user3", email="user3@example.com")

        self.voucher1 = Voucher.objects.create(
            by=self.user1,
            to=self.user2,
            value=1
        )
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

    def test_anonymous_cannot_list(self):
        """
        An anonymous user can't list received vouchers.
        """
        client = APIClient()

        response = client.get("/vouchers/received/", format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_list(self):
        """
        A user can list their received vouchers.
        """
        client = APIClient()
        client.force_authenticate(user=self.user3)

        response = client.get("/vouchers/received/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        self.assertEqual(len(results), 2)

        self.assertDictEqual(
            results[0],
            {
                "id": self.voucher2.id,
                "by": "user1",
                "is_public": True,
                "value": 2,
            },
            results[0],
        )

        self.assertDictEqual(
            results[1],
            {
                "id": self.voucher3.id,
                "by": "user2",
                "is_public": False,
                "value": 3,
            },
            results[1],
        )
