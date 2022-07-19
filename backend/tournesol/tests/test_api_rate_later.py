from unittest.mock import ANY, patch

from django.db import transaction
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from core.tests.factories.user import UserFactory
from tournesol.models import Entity, Poll, RateLater
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import RateLaterFactory, VideoFactory
from tournesol.tests.factories.poll import PollFactory


class RateLaterCommonMixinTestCase:
    """
    A mixin that factorizes utility functions common to all rate-later test
    cases.
    """

    _user = "username"
    _invalid_poll_name = "invalid"

    _uid_not_in_db = "yt:xSqqXN0D4fY"

    def common_set_up(self) -> None:
        self.maxDiff = None

        self.client = APIClient()
        self.user = UserFactory(username=self._user)

        self.poll = PollFactory()
        self.rate_later_base_url = f"/users/me/rate_later/{self.poll.name}/"

        self.entity_in_ratelater = VideoFactory()
        self.entity_not_in_ratelater = VideoFactory()

        self.to_rate_later = RateLater.objects.create(
            entity=self.entity_in_ratelater,
            user=self.user,
            poll=self.poll,
        )


class RateLaterListTestCase(RateLaterCommonMixinTestCase, TestCase):
    """
    TestCase of the `RateLaterList` API.

    The `RateLaterList` API provides the endpoints list and create.
    """

    def setUp(self) -> None:
        self.common_set_up()

    def test_anon_401_list(self) -> None:
        """
        An anonymous user cannot list its rate-later items, even if the poll
        exists.
        """
        response = self.client.get(self.rate_later_base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anon_401_list_invalid_poll(self) -> None:
        """
        An anonymous user cannot list its rate-later items, even if the poll
        doesn't exist.
        """
        response = self.client.get(f"/users/me/rate_later/{self._invalid_poll_name}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_200_list(self) -> None:
        """
        An authenticated user can list its rate-later items from a specific
        poll.
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(self.rate_later_base_url)

        results = response.data["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        self.assertDictEqual(
            results[0],
            {
                "entity": {
                    "uid": self.to_rate_later.entity.uid,
                    "type": "video",
                    "metadata": ANY,
                },
                "created_at": str(
                    self.to_rate_later.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                ),
            },
            results[0],
        )

    def test_auth_200_list_is_poll_specific(self) -> None:
        """
        Rate-later items are saved per poll.
        """
        other_poll = PollFactory()
        RateLater.objects.create(
            entity=self.entity_not_in_ratelater,
            user=self.user,
            poll=other_poll,
        )

        # The rate-later list of the poll `self.poll` must contain only the
        # entity `self.entity_in_ratelater`.
        self.client.force_authenticate(self.user)
        response = self.client.get(self.rate_later_base_url)
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(results[0]["entity"]["uid"], self.entity_in_ratelater.uid)

        # The rate-later list of the poll `other_poll` must contain only the
        # entity `self.entity_not_in_ratelater`.
        response = self.client.get(f"/users/me/rate_later/{other_poll.name}/")
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(results[0]["entity"]["uid"], self.entity_not_in_ratelater.uid)

    def test_auth_404_list_invalid_poll(self) -> None:
        """
        An authenticated user cannot list its rate-later items from a
        non-existing poll.
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(f"/users/me/rate_later/{self._invalid_poll_name}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anon_401_create(self) -> None:
        """
        An anonymous user cannot add an entity to its rate-later list, even if
        the poll exists.
        """
        data = {"entity": {"uid": "yt:xSqqXN0D4fY"}}
        response = self.client.post(self.rate_later_base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anon_401_create_invalid_poll(self) -> None:
        """
        An anonymous user cannot add an entity to its rate-later list, even if
        the poll doesn't exist.
        """
        data = {"entity": {"uid": "yt:xSqqXN0D4fY"}}
        response = self.client.post(
            f"/users/me/rate_later/{self._invalid_poll_name}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("tournesol.utils.api_youtube.YOUTUBE", None)
    def test_auth_201_create(self) -> None:
        """
        An authenticated user can add an entity to its rate-later list from a
        specific poll, even if the entity doesn't exist in the database yet.
        """
        # A second poll ensures the create operation is poll specific.
        other_poll = PollFactory()
        initial_nbr = RateLater.objects.filter(poll=self.poll, user=self.user).count()

        self.client.force_authenticate(self.user)
        data = {"entity": {"uid": self._uid_not_in_db}}
        response = self.client.post(self.rate_later_base_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            RateLater.objects.filter(poll=self.poll, user=self.user).count(),
            initial_nbr + 1,
        )

        # Rate-later items are saved per poll.
        self.assertEqual(
            RateLater.objects.filter(poll=other_poll, user=self.user).count(), 0
        )

    @patch("tournesol.utils.api_youtube.YOUTUBE", None)
    def test_auth_409_create_two_times(self) -> None:
        """
        An authenticated user cannot add two times the same entity to a
        rate-later list of a specific poll.
        """
        other_poll = PollFactory()

        self.client.force_authenticate(self.user)
        data = {"entity": {"uid": self.entity_in_ratelater.uid}}

        with transaction.atomic():
            response = self.client.post(self.rate_later_base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # A user can add the same entity in rate-later lists of different
        # polls.
        response = self.client.post(
            f"/users/me/rate_later/{other_poll.name}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auth_404_create_invalid_poll(self) -> None:
        """
        An authenticated user cannot add an entity in a rate-later list from a
        non-existing poll.
        """
        self.client.force_authenticate(self.user)
        data = {"entity": {"uid": "yt:xSqqXN0D4fY"}}
        response = self.client.post(
            f"/users/me/rate_later/{self._invalid_poll_name}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RateLaterDetailTestCase(RateLaterCommonMixinTestCase, TestCase):
    """
    TestCase of the `RateLaterDetail` API.

    The `RateLaterList` API provides the endpoints get and delete.
    """

    def setUp(self) -> None:
        self.common_set_up()

    def test_anon_401_get(self) -> None:
        """
        An anonymous user cannot get a rate-later item, even if the poll
        exists.
        """
        response = self.client.get(
            f"{self.rate_later_base_url}{self.entity_in_ratelater.uid}/"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(f"{self.rate_later_base_url}invalid/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anon_401_get_invalid_poll(self) -> None:
        """
        An anonymous user cannot get a rate-later item, even if the poll
        doesn't exist.
        """
        response = self.client.get(
            f"/users/me/rate_later/{self._invalid_poll_name}{self.entity_in_ratelater.uid}/"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_200_get(self) -> None:
        """
        An authenticated user can get a rate-later item from a specific poll.
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(
            f"{self.rate_later_base_url}{self.entity_in_ratelater.uid}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictEqual(
            response.data,
            {
                "entity": {
                    "uid": self.to_rate_later.entity.uid,
                    "type": "video",
                    "metadata": ANY,
                },
                "created_at": str(
                    self.to_rate_later.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                ),
            },
        )

    def test_auth_200_get_is_poll_specific(self) -> None:
        """
        Rate-later items are saved per poll.
        """
        other_poll = PollFactory()
        RateLater.objects.create(
            entity=self.entity_not_in_ratelater,
            user=self.user,
            poll=other_poll,
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(
            f"{self.rate_later_base_url}{self.entity_in_ratelater.uid}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            f"/users/me/rate_later/{other_poll.name}/{self.entity_in_ratelater.uid}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_auth_404_get_invalid_poll(self) -> None:
        """
        An authenticated user cannot get a rate-later item from a non-existing
        poll.
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(
            f"/users/me/rate_later/{self._invalid_poll_name}{self.entity_in_ratelater.uid}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anon_401_delete(self) -> None:
        """
        An anonymous user cannot delete an item from its rate-later list, even
        if the poll exists.
        """
        response = self.client.delete(
            f"{self.rate_later_base_url}{self.entity_in_ratelater.uid}/"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(f"{self.rate_later_base_url}invalid/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anon_401_delete_invalid_poll(self) -> None:
        """
        An anonymous user cannot delete an item from its rate-later list, even
        if the poll doesn't exist.
        """
        response = self.client.delete(
            f"/users/me/rate_later/{self._invalid_poll_name}/{self.entity_in_ratelater.uid}/"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_201_delete(self) -> None:
        """
        An authenticated user can delete an item from its rate-later list.
        """
        # A second poll ensures the delete operation is poll specific.
        other_poll = PollFactory()
        RateLater.objects.create(
            entity=self.entity_in_ratelater, user=self.user, poll=other_poll
        )

        initial_nbr = RateLater.objects.filter(poll=self.poll, user=self.user).count()

        self.client.force_authenticate(self.user)
        response = self.client.delete(
            f"{self.rate_later_base_url}{self.entity_in_ratelater.uid}/"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            RateLater.objects.filter(poll=self.poll, user=self.user).count(),
            initial_nbr - 1,
        )

        # Rate-later items are saved per poll.
        self.assertEqual(
            RateLater.objects.filter(poll=other_poll, user=self.user).count(), 1
        )

    def test_auth_404_delete_invalid_poll(self) -> None:
        """
        An authenticated user cannot delete a rate-later item from a
        non-existing poll.
        """
        self.client.force_authenticate(self.user)
        response = self.client.delete(
            f"/users/me/rate_later/{self._invalid_poll_name}/{self.entity_in_ratelater.uid}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RateLaterFeaturesTestCase(RateLaterCommonMixinTestCase, TestCase):
    """
    TestCase of extra features related to the rate-later models.

    Note: the tests related to `Entity.auto_remove_from_rate_later` could be
    moved in an Entity specific test case.
    """

    def setUp(self) -> None:
        self.common_set_up()

    def test_auto_remove(self) -> None:
        """
        Test of the `auto_remove_from_rate_later` method of the Entity model.

        After 4 comparisons, calling the tested method must remove the entity
        from the user's rate-later list related to the specified poll.
        """
        poll = self.poll
        user = self.user
        entity = self.entity_in_ratelater

        # Initial state.
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            1,
        )

        # The entity must not be removed after 2 comparisons.
        ComparisonFactory(poll=poll, user=user, entity_1=entity)
        ComparisonFactory(poll=poll, user=user, entity_1=entity)
        entity.auto_remove_from_rate_later(poll, user)
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            1,
        )

        # The entity must not be removed after 3 comparisons.
        ComparisonFactory(poll=poll, user=user, entity_2=entity)
        entity.auto_remove_from_rate_later(poll, user)
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            1,
        )

        # The entity must not be removed when comparing unrelated videos.
        ComparisonFactory(poll=poll, user=user)
        ComparisonFactory(poll=poll, user=user)
        entity.auto_remove_from_rate_later(poll, user)
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            1,
        )

        # The entity must be removed after 4 comparisons.
        ComparisonFactory(poll=poll, user=user, entity_2=entity)
        entity.auto_remove_from_rate_later(poll, user)
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            0,
        )

        # The entity can be added again.
        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.rate_later_base_url,
            {"entity": {"uid": entity.uid}},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            1,
        )

        # The entity is removed again after one new comparison.
        ComparisonFactory(poll=poll, user=user, entity_2=entity)
        entity.auto_remove_from_rate_later(poll, user)
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            0,
        )

    def test_auto_remove_is_user_specific(self) -> None:
        """
        Test of the `auto_remove_from_rate_later` method of the Entity model.

        Calling the tested method must affect only the rate-later list of the
        given user.
        """
        poll = self.poll
        user = self.user
        other_user = self.user = UserFactory(username="other_user")
        entity = self.entity_in_ratelater

        # Initial state.
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            1,
        )

        # The entity must not be removed when compared by other users.
        ComparisonFactory(user=other_user, entity_1=entity)
        ComparisonFactory(user=other_user, entity_1=entity)
        ComparisonFactory(user=other_user, entity_2=entity)
        ComparisonFactory(user=other_user, entity_2=entity)
        entity.auto_remove_from_rate_later(poll, user)
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            1,
        )

    def test_auto_remove_is_poll_specific(self) -> None:
        """
        Test of the `auto_remove_from_rate_later` method of the Entity model.

        Calling the tested method must affect only the rate-later list of the
        given poll.
        """
        poll = self.poll
        other_poll = PollFactory()
        user = self.user
        entity = self.entity_in_ratelater

        RateLater.objects.create(
            entity=entity,
            user=self.user,
            poll=other_poll,
        )

        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            1,
        )

        # The entity must be removed only from the rate-later list related to poll in
        # which the 4 comparison are made.
        ComparisonFactory(poll=poll, user=user, entity_1=entity)
        ComparisonFactory(poll=poll, user=user, entity_1=entity)
        ComparisonFactory(poll=poll, user=user, entity_2=entity)
        ComparisonFactory(poll=poll, user=user, entity_2=entity)
        entity.auto_remove_from_rate_later(poll, user)
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            0,
        )
        # The other rate-later lists must not be affected.
        self.assertEqual(
            RateLater.objects.filter(poll=other_poll, user=user, entity=entity).count(),
            1,
        )
