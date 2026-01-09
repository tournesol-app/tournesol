from concurrent.futures import ThreadPoolExecutor
from unittest.mock import ANY

from django.db import connection, transaction
from django.test import TestCase, TransactionTestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models import RateLater
from tournesol.models.entity_context import EntityContext, EntityContextLocale
from tournesol.models.ratings import ContributorRating
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.entity_poll_rating import EntityPollRatingFactory
from tournesol.tests.factories.poll import PollFactory
from tournesol.tests.factories.ratings import ContributorRatingFactory
from tournesol.utils.constants import RATE_LATER_BULK_MAX_SIZE


class RateLaterCommonMixinTestCase:
    """
    A mixin that factorizes utility functions common to all rate-later test
    cases.
    """

    _user = "username"
    _invalid_poll_name = "invalid"

    _uid_not_in_db = "yt:xSqqXN0D4fY"

    def setUp(self) -> None:
        self.maxDiff = None

        self.client = APIClient()
        self.user = UserFactory(username=self._user)

        self.poll = PollFactory()
        self.rate_later_base_url = f"/users/me/rate_later/{self.poll.name}/"
        self.rate_later_bulk_base_url = f"/users/me/rate_later/{self.poll.name}/_bulk_create"

        self.entity_in_ratelater = VideoFactory()

        EntityPollRatingFactory(
            entity=self.entity_in_ratelater,
            poll=self.poll,
            tournesol_score=3,
            n_contributors=1,
            n_comparisons=2,
        )

        self.entity_in_rl_context = EntityContext.objects.create(
            name="context_safe",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.entity_in_ratelater.metadata["video_id"]},
            unsafe=False,
            enabled=True,
            poll=self.poll,
        )

        self.entity_in_rl_context_text = EntityContextLocale.objects.create(
            context=self.entity_in_rl_context,
            language="en",
            text="Hello context",
        )

        self.entity_not_in_ratelater = VideoFactory()

        self.to_rate_later = RateLater.objects.create(
            entity=self.entity_in_ratelater,
            user=self.user,
            poll=self.poll,
        )


class RateLaterListTestCase(RateLaterCommonMixinTestCase, TransactionTestCase):
    """
    TestCase of the `RateLaterList` API.

    The `RateLaterList` API provides the endpoints list and create.
    """

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
                "entity_contexts": [
                    {
                        "origin": "ASSOCIATION",
                        "unsafe": False,
                        "text": self.entity_in_rl_context_text.text,
                        "created_at": self.entity_in_rl_context.created_at.strftime(
                            "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                    }
                ],
                "individual_rating": None,
                "collective_rating": {
                    "n_comparisons": 2,
                    "n_contributors": 1,
                    "tournesol_score": 3.0,
                    "unsafe": {
                        "status": True,
                        "reasons": ANY,
                    },
                },
                "rate_later_metadata": {
                    "created_at": str(
                        self.to_rate_later.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    ),
                },
            },
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

    @override_settings(YOUTUBE_API_KEY=None)
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
        self.assertDictEqual(
            response.data,
            {
                "entity": {
                    "uid": self._uid_not_in_db,
                    "type": "video",
                    "metadata": ANY,
                },
                "entity_contexts": [],
                "collective_rating": None,
                "individual_rating": None,
                "rate_later_metadata": {"created_at": ANY},
            },
        )

        self.assertEqual(
            RateLater.objects.filter(poll=self.poll, user=self.user).count(),
            initial_nbr + 1,
        )

        # Rate-later items are saved per poll.
        self.assertEqual(RateLater.objects.filter(poll=other_poll, user=self.user).count(), 0)


    @override_settings(YOUTUBE_API_KEY=None)
    def test_auth_201_create_with_param_entity_seen(self) -> None:
        """
        An authenticated user can add an entity to its rate-later list and
        mark it as seen/watched/etc.
        """
        initial_nbr = RateLater.objects.filter(poll=self.poll, user=self.user).count()

        self.assertEqual(
            ContributorRating.objects.filter(poll=self.poll, user=self.user).count(),
            0
        )

        self.client.force_authenticate(self.user)
        data = {"entity": {"uid": self._uid_not_in_db}}
        response = self.client.post(self.rate_later_base_url + "?entity_seen=true", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            RateLater.objects.filter(poll=self.poll, user=self.user).count(),
            initial_nbr + 1,
        )

        ratings = ContributorRating.objects.filter(poll=self.poll, user=self.user)
        rating = ratings[0]
        self.assertEqual(ratings.count(), 1)
        # By default, the rate-later API should set the `is_public` field to True.
        self.assertEqual(rating.is_public, True)
        self.assertEqual(rating.entity_seen, True)


    @override_settings(YOUTUBE_API_KEY=None)
    def test_auth_201_create_with_param_entity_seen_and_existing_rating(self) -> None:
        """
        An authenticated user can add an entity to its rate-later list and
        mark it as seen/watched/etc., even if the related ContributorRating
        already exists.
        """
        self.client.force_authenticate(self.user)
        data = {"entity": {"uid": self._uid_not_in_db}}
        response = self.client.post(self.rate_later_base_url + "?entity_seen=true", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rating = ContributorRating.objects.get(poll=self.poll, user=self.user, entity__uid=self._uid_not_in_db)
        self.assertEqual(rating.is_public, True)
        self.assertEqual(rating.entity_seen, True)

        rating.is_public = False
        rating.entity_seen = False
        rating.save(update_fields=["entity_seen", "is_public"])
        RateLater.objects.filter(user=self.user).delete()

        response = self.client.post(self.rate_later_base_url + "?entity_seen=true", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rating.refresh_from_db()
        # Only the `entity_seen` field should be updated.
        self.assertEqual(rating.is_public, False)
        self.assertEqual(rating.entity_seen, True)


    @override_settings(YOUTUBE_API_KEY=None)
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


class RateLaterBulkCreateTestCase(RateLaterCommonMixinTestCase, TestCase):
    """
    TestCase of the `RateLaterBulkCreate` API.

    The `RateLaterBulkCreate` API provides an endpoint to add multiple
    entities to the rate-later list.
    """

    _other_uid_not_in_db = "yt:n-oujbO9fdQ"

    def test_anon_401_create(self) -> None:
        """
        An anonymous user cannot add entities to its rate-later list, even if
        the poll exists.
        """
        data = [
            {"entity": {"uid": self._uid_not_in_db}},
            {"entity": {"uid": self._other_uid_not_in_db}},
        ]
        response = self.client.post(self.rate_later_bulk_base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anon_401_create_invalid_poll(self) -> None:
        """
        An anonymous user cannot add entities to its rate-later list, even if
        the poll doesn't exist.
        """
        data = [
            {"entity": {"uid": self._uid_not_in_db}},
            {"entity": {"uid": self._other_uid_not_in_db}},
        ]
        response = self.client.post(
            f"/users/me/rate_later/{self._invalid_poll_name}/_bulk_create", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(YOUTUBE_API_KEY=None)
    def test_auth_201_create(self) -> None:
        """
        An authenticated user can add entities to its rate-later list from a
        specific poll, even if the entity doesn't exist in the database yet.
        """
        # A second poll ensures the create operation is poll specific.
        other_poll = PollFactory()
        initial_nbr = RateLater.objects.filter(poll=self.poll, user=self.user).count()

        self.client.force_authenticate(self.user)
        data = [
            {"entity": {"uid": self._uid_not_in_db}},
            {"entity": {"uid": self._other_uid_not_in_db}},
        ]
        response = self.client.post(self.rate_later_bulk_base_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertListEqual(
            response.data,
            [
                {
                    "entity": {
                        "uid": self._uid_not_in_db,
                        "type": "video",
                        "metadata": ANY,
                    },
                    "entity_contexts": [],
                    "collective_rating": None,
                    "individual_rating": None,
                    "rate_later_metadata": {"created_at": ANY},
                },
                {
                    "entity": {
                        "uid": self._other_uid_not_in_db,
                        "type": "video",
                        "metadata": ANY,
                    },
                    "entity_contexts": [],
                    "collective_rating": None,
                    "individual_rating": None,
                    "rate_later_metadata": {"created_at": ANY},
                },
            ],
        )

        self.assertEqual(
            RateLater.objects.filter(poll=self.poll, user=self.user).count(),
            initial_nbr + 2,
        )

        # Rate-later items are saved per poll.
        self.assertEqual(RateLater.objects.filter(poll=other_poll, user=self.user).count(), 0)

    @override_settings(YOUTUBE_API_KEY=None)
    def test_auth_201_create_two_times(self) -> None:
        """
        An authenticated user can request to add two times the same entity to a
        rate-later list of a specific poll. In this case the duplicates are ignored.
        """
        other_poll = PollFactory()
        initial_nbr = RateLater.objects.filter(poll=self.poll, user=self.user).count()

        self.client.force_authenticate(self.user)
        data = [
            {"entity": {"uid": self.entity_in_ratelater.uid}},
            {"entity": {"uid": self._uid_not_in_db}},
        ]

        response = self.client.post(self.rate_later_bulk_base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertListEqual(
            response.data,
            [
                {
                    "entity": {
                        "uid": self._uid_not_in_db,
                        "type": "video",
                        "metadata": ANY,
                    },
                    "entity_contexts": [],
                    "collective_rating": None,
                    "individual_rating": None,
                    "rate_later_metadata": {"created_at": ANY},
                },
            ],
        )
        self.assertEqual(
            RateLater.objects.filter(poll=self.poll, user=self.user).count(),
            initial_nbr + 1,
        )

    @override_settings(YOUTUBE_API_KEY=None)
    def test_auth_201_create_with_param_entity_seen(self) -> None:
        self.client.force_authenticate(self.user)
        data = [
            {"entity": {"uid": self._uid_not_in_db}},
            {"entity": {"uid": self._other_uid_not_in_db}},
        ]

        self.assertEqual(
            ContributorRating.objects.filter(poll=self.poll, user=self.user).count(),
            0
        )

        response = self.client.post(
            self.rate_later_bulk_base_url + "?entity_seen=true", data, format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(
            response.data[0]["individual_rating"],
            {"is_public": True, "entity_seen": True, 'n_comparisons': 0}
        )
        self.assertDictEqual(
            response.data[1]["individual_rating"],
            {"is_public": True, "entity_seen": True, 'n_comparisons': 0}
        )
        self.assertEqual(
            ContributorRating.objects.filter(poll=self.poll, user=self.user).count(),
            2
        )

        # To respect the users' choices, a bulk create must not update the
        # `is_public` value of existing contributor ratings.
        ContributorRating.objects.update(entity_seen=False, is_public=False)
        response = self.client.post(
            self.rate_later_bulk_base_url + "?entity_seen=true", data, format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, [])
        c_ratings = ContributorRating.objects.filter(poll=self.poll, user=self.user)
        self.assertEqual(c_ratings[0].is_public, False)
        self.assertEqual(c_ratings[1].is_public, False)
        self.assertEqual(c_ratings[0].entity_seen, True)
        self.assertEqual(c_ratings[1].entity_seen, True)

    @override_settings(YOUTUBE_API_KEY=None)
    def test_create_size_limit(self) -> None:
        """
        An authenticated user can only add a limited number of entities.
        """
        self.client.force_authenticate(self.user)

        limit = RATE_LATER_BULK_MAX_SIZE

        initial_nbr = RateLater.objects.filter(poll=self.poll, user=self.user).count()
        data = [{"entity": {"uid": "yt:entity1-{:03d}".format(n)}} for n in range(limit)]
        response = self.client.post(self.rate_later_bulk_base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            RateLater.objects.filter(poll=self.poll, user=self.user).count(),
            initial_nbr + 20,
        )

        initial_nbr = RateLater.objects.filter(poll=self.poll, user=self.user).count()
        data = [{"entity": {"uid": "yt:entity2-{:03d}".format(n)}} for n in range(limit + 1)]
        response = self.client.post(self.rate_later_bulk_base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            RateLater.objects.filter(poll=self.poll, user=self.user).count(),
            initial_nbr,
        )

    def test_auth_404_create_invalid_poll(self) -> None:
        """
        An authenticated user cannot add entities in a rate-later list from a
        non-existing poll.
        """
        self.client.force_authenticate(self.user)
        data = [
            {"entity": {"uid": self._uid_not_in_db}},
            {"entity": {"uid": self._other_uid_not_in_db}},
        ]
        response = self.client.post(
            f"/users/me/rate_later/{self._invalid_poll_name}/_bulk_create", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RateLaterDetailTestCase(RateLaterCommonMixinTestCase, TestCase):
    """
    TestCase of the `RateLaterDetail` API.

    The `RateLaterList` API provides the endpoints get and delete.
    """

    def test_anon_401_get(self) -> None:
        """
        An anonymous user cannot get a rate-later item, even if the poll
        exists.
        """
        response = self.client.get(f"{self.rate_later_base_url}{self.entity_in_ratelater.uid}/")
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
        response = self.client.get(f"{self.rate_later_base_url}{self.entity_in_ratelater.uid}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictEqual(
            response.data,
            {
                "entity": {
                    "uid": self.to_rate_later.entity.uid,
                    "type": "video",
                    "metadata": ANY,
                },
                "entity_contexts": [
                    {
                        "origin": "ASSOCIATION",
                        "unsafe": False,
                        "text": self.entity_in_rl_context_text.text,
                        "created_at": self.entity_in_rl_context.created_at.strftime(
                            "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                    }
                ],
                "individual_rating": None,
                "collective_rating": {
                    "n_comparisons": 2,
                    "n_contributors": 1,
                    "tournesol_score": 3.0,
                    "unsafe": {
                        "status": True,
                        "reasons": ANY,
                    },
                },
                "rate_later_metadata": {
                    "created_at": self.to_rate_later.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                },
            },
        )

    def test_auth_200_get_with_contributor_rating(self) -> None:
        """
        An authenticated user can get a rate-later item from a specific poll.
        """
        ContributorRatingFactory(
            user=self.user,
            poll=self.poll,
            entity=self.entity_in_ratelater,
            is_public=True,
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(f"{self.rate_later_base_url}{self.entity_in_ratelater.uid}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictEqual(
            response.data,
            {
                "entity": {
                    "uid": self.to_rate_later.entity.uid,
                    "type": "video",
                    "metadata": ANY,
                },
                "entity_contexts": [
                    {
                        "origin": "ASSOCIATION",
                        "unsafe": False,
                        "text": self.entity_in_rl_context_text.text,
                        "created_at": self.entity_in_rl_context.created_at.strftime(
                            "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                    }
                ],
                "individual_rating": {
                    "is_public": True,
                    "entity_seen": False,
                    "n_comparisons": 0,
                },
                "collective_rating": {
                    "n_comparisons": 2,
                    "n_contributors": 1,
                    "tournesol_score": 3.0,
                    "unsafe": {
                        "status": True,
                        "reasons": ANY,
                    },
                },
                "rate_later_metadata": {
                    "created_at": self.to_rate_later.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                },
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
        response = self.client.get(f"{self.rate_later_base_url}{self.entity_in_ratelater.uid}/")
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
        response = self.client.delete(f"{self.rate_later_base_url}{self.entity_in_ratelater.uid}/")
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

    def test_auth_204_delete(self) -> None:
        """
        An authenticated user can delete an item from its rate-later list.
        """
        # A second poll ensures the delete operation is poll specific.
        other_poll = PollFactory()
        RateLater.objects.create(entity=self.entity_in_ratelater, user=self.user, poll=other_poll)

        initial_nbr = RateLater.objects.filter(poll=self.poll, user=self.user).count()

        self.client.force_authenticate(self.user)
        response = self.client.delete(f"{self.rate_later_base_url}{self.entity_in_ratelater.uid}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            RateLater.objects.filter(poll=self.poll, user=self.user).count(),
            initial_nbr - 1,
        )

        # Rate-later items are saved per poll.
        self.assertEqual(RateLater.objects.filter(poll=other_poll, user=self.user).count(), 1)

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

    def test_auto_remove(self) -> None:
        """
        Test of the `auto_remove_from_rate_later` method of the Entity model.

        After a defined number of comparisons, calling the tested method must
        remove the entity from the user's rate-later list related to the
        specified poll.
        """
        poll = self.poll
        user = self.user
        entity = self.entity_in_ratelater

        # [GIVEN] a user without settings.
        user.settings = {}
        user.save(update_fields=["settings"])

        # [GIVEN] a rate-later list with 1 entity.
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
        self.assertDictEqual(
            response.data["individual_rating"],
            {
                "is_public": False,
                "entity_seen": True,
                "n_comparisons": 4,
            },
        )
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

    def test_auto_remove_is_setting_specific(self) -> None:
        """
        Test of the `auto_remove_from_rate_later` method of the Entity model.

        After number of comparisons defined by the user's settings, calling
        the tested method must remove the entity from the user's rate-later
        list.
        """
        poll = self.poll
        user = self.user
        entity = self.entity_in_ratelater

        # [GIVEN] a user with the setting `auto_remove` set to 2.
        user.settings[poll.name] = {"rate_later__auto_remove": 2}
        user.save(update_fields=["settings"])

        # [GIVEN] a rate-later list with 1 entity.
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            1,
        )

        # [WHEN] the entity is compared 1 time.
        ComparisonFactory(poll=poll, user=user, entity_1=entity)
        entity.auto_remove_from_rate_later(poll, user)

        # [THEN] the entity should be present in the rate-later list.
        self.assertEqual(
            RateLater.objects.filter(poll=poll, user=user, entity=entity).count(),
            1,
        )

        # [WHEN] the entity is compared 2 tims.
        ComparisonFactory(poll=poll, user=user, entity_1=entity)
        entity.auto_remove_from_rate_later(poll, user)

        # [THEN] the entity should not be present in the rate-later list.
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


class TestConcurrentRequests(RateLaterCommonMixinTestCase, TransactionTestCase):
    @override_settings(YOUTUBE_API_KEY=None)
    def test_simultaneous_requests(self):
        data = {"entity": {"uid": self._uid_not_in_db}}

        def add_to_rate_later():
            user = UserFactory()
            client = APIClient()
            client.force_authenticate(user)
            response = client.post(self.rate_later_base_url, data, format="json")
            connection.close()  # Make sure that db connection is closed in the current thread
            return response

        with ThreadPoolExecutor() as executor:
            thread1 = executor.submit(add_to_rate_later)
            thread2 = executor.submit(add_to_rate_later)

        self.assertEqual(thread1.result().status_code, status.HTTP_201_CREATED)
        self.assertEqual(thread2.result().status_code, status.HTTP_201_CREATED)
