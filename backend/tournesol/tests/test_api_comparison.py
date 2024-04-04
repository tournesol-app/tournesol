import datetime
from copy import deepcopy
from unittest.mock import patch

from django.core.management import call_command
from django.db.models import ObjectDoesNotExist, Q
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from core.utils.time import time_ago, time_ahead
from tournesol.models import (
    Comparison,
    ContributorRatingCriteriaScore,
    Entity,
    EntityCriteriaScore,
    EntityPollRating,
    Poll,
    RateLater,
)
from tournesol.models.entity_context import EntityContext, EntityContextLocale
from tournesol.models.poll import ALGORITHM_MEHESTAN
from tournesol.tests.factories.comparison import ComparisonCriteriaScoreFactory, ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.poll import CriteriaRankFactory, PollFactory


class ComparisonApiTestCase(TestCase):
    """
    TestCase of the comparison API.

    For each endpoint, the test case checks:
        - authorizations
        - permissions
        - behaviour
    """

    _user = "username"
    _other = "other_username"

    # videos available in all tests
    _uid_01 = "yt:video_id_01"
    _uid_02 = "yt:video_id_02"
    _uid_03 = "yt:video_id_03"
    _uid_04 = "yt:video_id_04"

    # non-existing videos that can be created
    _uid_05 = "yt:video_id_05"
    _uid_06 = "yt:video_id_06"
    _uid_07 = "yt:video_id_07"

    non_existing_comparison = {
        "entity_a": {"uid": _uid_01},
        "entity_b": {"uid": _uid_03},
        "criteria_scores": [{"criteria": "largely_recommended", "score": 10, "weight": 10}],
        "duration_ms": 103,
    }

    def setUp(self):
        """
        Set up a minimal set of data to test the ComparisonList API.

        At least 4 videos and 2 users with 2 comparisons each are required.
        """
        self.poll_videos = Poll.default_poll()
        self.comparisons_base_url = "/users/me/comparisons/{}".format(self.poll_videos.name)

        self.client = APIClient()

        self.user = UserFactory(username=self._user)
        self.other = UserFactory(username=self._other)
        now = datetime.datetime.now()

        self.videos = [
            VideoFactory(metadata__video_id=self._uid_01.split(":")[1], make_safe_for_poll=False),
            VideoFactory(metadata__video_id=self._uid_02.split(":")[1], make_safe_for_poll=False),
            VideoFactory(metadata__video_id=self._uid_03.split(":")[1], make_safe_for_poll=False),
            VideoFactory(metadata__video_id=self._uid_04.split(":")[1], make_safe_for_poll=False),
        ]

        self.comparisons = [
            # "user" will have the comparisons: 01 / 02 and 01 / 04
            ComparisonFactory(
                user=self.user,
                entity_1=self.videos[0],
                entity_2=self.videos[1],
                duration_ms=102,
                datetime_lastedit=now,
            ),
            ComparisonFactory(
                user=self.user,
                entity_1=self.videos[0],
                entity_2=self.videos[3],
                duration_ms=104,
                datetime_lastedit=time_ahead(minutes=1),
            ),
            # "other" will have the comparisons: 03 / 02 and 03 / 04
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[2],
                entity_2=self.videos[1],
                duration_ms=302,
                datetime_lastedit=time_ahead(minutes=3),
            ),
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[2],
                entity_2=self.videos[3],
                duration_ms=304,
                datetime_lastedit=time_ahead(minutes=2),
            ),
        ]

        self.ent_context_01 = EntityContext.objects.create(
            name="context_safe",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.videos[0].metadata["video_id"]},
            unsafe=False,
            enabled=True,
            poll=self.poll_videos,
        )

        self.ent_context_01_text = EntityContextLocale.objects.create(
            context=self.ent_context_01,
            language="en",
            text="Hello context",
        )

    def _remove_optional_fields(self, comparison):
        comparison.pop("duration_ms", None)

        if "criteria_scores" in comparison:
            for criteria_score in comparison["criteria_scores"]:
                criteria_score.pop("weight", None)

        return comparison

    def _compare(self, uid_1, uid_2):
        self.client.post(
            self.comparisons_base_url,
            {
                "entity_a": {"uid": uid_1},
                "entity_b": {"uid": uid_2},
                "criteria_scores": [
                    {"criteria": "largely_recommended", "score": 10, "weight": 10}
                ],
                "duration_ms": 103,
            },
            format="json",
        )

    def test_anonymous_cant_create(self):
        """
        An anonymous user can't create a comparison.
        """
        initial_comparisons_nbr = Comparison.objects.all().count()
        data = deepcopy(self.non_existing_comparison)

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        comparisons = Comparison.objects.filter(
            entity_1__uid=self._uid_01, entity_2__uid=self._uid_03
        )
        self.assertFalse(comparisons.exists())

        comparisons = Comparison.objects.filter(
            entity_1__uid=self._uid_03, entity_2__uid=self._uid_01
        )
        self.assertFalse(comparisons.exists())
        self.assertEqual(Comparison.objects.all().count(), initial_comparisons_nbr)

    def test_authenticated_cant_create_non_existing_poll(self):
        """
        An authenticated user can't create a comparison in a non-existing
        poll.
        """
        self.client.force_authenticate(user=self.user)
        data = deepcopy(self.non_existing_comparison)
        non_existing_poll = "non-existing"

        response = self.client.post(
            "/users/me/comparisons/{}/".format(non_existing_poll),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # the non-existing poll must not be created
        with self.assertRaises(ObjectDoesNotExist):
            Comparison.objects.select_related(
                "user", "poll", "entity_1", "entity_2"
            ).get(
                user=self.user,
                poll__name=non_existing_poll,
                entity_1__uid=data["entity_a"]["uid"],
                entity_2__uid=data["entity_b"]["uid"],
            )

        # the default poll must not contain the comparison
        with self.assertRaises(ObjectDoesNotExist):
            Comparison.objects.select_related(
                "user", "poll", "entity_1", "entity_2"
            ).get(
                user=self.user,
                poll=self.poll_videos,
                entity_1__uid=data["entity_a"]["uid"],
                entity_2__uid=data["entity_b"]["uid"],
            )

    def test_authenticated_can_create(self):
        """
        An authenticated user can create a new comparison.

        Ensure the database object contains the data sent.

        Also ensure the object representation included in the API response
        contains the data sent.
        """
        initial_comparisons_nbr = Comparison.objects.filter(user=self.user).count()
        data = deepcopy(self.non_existing_comparison)

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )
        # check the authorization
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        comparison = Comparison.objects.select_related(
            "user", "entity_1", "entity_2"
        ).get(
            user=self.user,
            poll=self.poll_videos,
            entity_1__uid=data["entity_a"]["uid"],
            entity_2__uid=data["entity_b"]["uid"],
        )
        comparisons_nbr = Comparison.objects.filter(user=self.user).count()

        # check the database integrity
        self.assertEqual(comparisons_nbr, initial_comparisons_nbr + 1)

        self.assertEqual(comparison.poll, self.poll_videos)
        self.assertEqual(comparison.user, self.user)
        self.assertEqual(comparison.entity_1.uid, data["entity_a"]["uid"])
        self.assertEqual(comparison.entity_2.uid, data["entity_b"]["uid"])
        self.assertEqual(comparison.duration_ms, data["duration_ms"])

        comparison_criteria_scores = comparison.criteria_scores.all()
        self.assertEqual(comparison_criteria_scores.count(), len(data["criteria_scores"]))
        self.assertEqual(
            comparison_criteria_scores[0].criteria,
            data["criteria_scores"][0]["criteria"],
        )
        self.assertEqual(comparison_criteria_scores[0].score, data["criteria_scores"][0]["score"])
        self.assertEqual(
            comparison_criteria_scores[0].weight, data["criteria_scores"][0]["weight"]
        )

        # check the representation integrity
        resp_data = response.data
        self.assertEqual(resp_data["entity_a"]["uid"], data["entity_a"]["uid"])
        self.assertEqual(resp_data["entity_b"]["uid"], data["entity_b"]["uid"])

        self.assertEqual(len(resp_data["entity_a_contexts"]), 1)
        self.assertEqual(resp_data["entity_a_contexts"][0]["text"], self.ent_context_01_text.text)
        self.assertEqual(resp_data["entity_b_contexts"], [])

        self.assertEqual(resp_data["duration_ms"], data["duration_ms"])

        self.assertEqual(len(response.data["criteria_scores"]), len(data["criteria_scores"]))
        self.assertEqual(
            response.data["criteria_scores"][0]["criteria"],
            data["criteria_scores"][0]["criteria"],
        )
        self.assertEqual(
            response.data["criteria_scores"][0]["score"],
            data["criteria_scores"][0]["score"],
        )
        self.assertEqual(
            response.data["criteria_scores"][0]["weight"],
            data["criteria_scores"][0]["weight"],
        )

    def test_creating_comparison_updates_the_ratings(self):
        """
        Ensure the `EntityPollRating`s are automatically created after each
        comparison.

        Also ensure these `EntityPollRating`s are updated if they already
        exist.
        """
        data = deepcopy(self.non_existing_comparison)
        self.client.force_authenticate(user=self.user)

        # Make sure `EntityPollRating`s don't exist yet.
        EntityPollRating.objects.filter(
            entity__uid__in=[
                self.non_existing_comparison["entity_a"]["uid"],
                self.non_existing_comparison["entity_b"]["uid"],
            ]
        ).delete()

        self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )

        # The `EntityPollRating`s have been created.
        rating_a = EntityPollRating.objects.get(
            entity__uid=self.non_existing_comparison["entity_a"]["uid"]
        )

        rating_b = EntityPollRating.objects.get(
            entity__uid=self.non_existing_comparison["entity_b"]["uid"]
        )

        self.assertEqual(rating_a.n_comparisons, 3)
        self.assertEqual(rating_a.n_contributors, 1)
        self.assertEqual(rating_b.n_comparisons, 3)
        self.assertEqual(rating_b.n_contributors, 2)

        self.client.force_authenticate(user=self.other)
        self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )

        rating_a.refresh_from_db()
        rating_b.refresh_from_db()

        # The `EntityPollRating`s have been updated.
        self.assertEqual(rating_a.n_comparisons, 4)
        self.assertEqual(rating_a.n_contributors, 2)
        self.assertEqual(rating_b.n_comparisons, 4)
        self.assertEqual(rating_b.n_contributors, 2)

    def test_authenticated_can_create_without_optional(self):
        """
        An authenticated user can create a new comparison with only required
        fields.

        All optional fields of the comparison and its related criteria are
        tested.
        """
        initial_comparisons_nbr = Comparison.objects.filter(user=self.user).count()
        data = self._remove_optional_fields(deepcopy(self.non_existing_comparison))

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )

        comparison = Comparison.objects.select_related(
            "user", "entity_1", "entity_2"
        ).get(
            poll=self.poll_videos,
            user=self.user,
            entity_1__uid=data["entity_a"]["uid"],
            entity_2__uid=data["entity_b"]["uid"],
        )
        comparisons_nbr = Comparison.objects.filter(user=self.user).count()

        # check the authorization
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check the database integrity (only the criteria scores part)
        self.assertEqual(comparisons_nbr, initial_comparisons_nbr + 1)

        self.assertEqual(
            comparison.duration_ms,
            Comparison._meta.get_field("duration_ms").get_default(),
        )

        comparison_criteria_scores = comparison.criteria_scores.all()
        self.assertEqual(comparison_criteria_scores.count(), len(data["criteria_scores"]))
        self.assertEqual(comparison_criteria_scores[0].weight, 1)

    @override_settings(YOUTUBE_API_KEY=None)
    def test_authenticated_can_create_with_non_existing_entity(self):
        """
        An authenticated user can create a comparison involving entities that
        are not present in the database yet.
        """
        initial_comparisons_nbr = Comparison.objects.filter(user=self.user).count()
        data = deepcopy(self.non_existing_comparison)
        # use the UID of a non-existing entity
        data["entity_a"]["uid"] = self._uid_05

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )
        # check the authorization
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        comparison = Comparison.objects.select_related(
            "user", "entity_1", "entity_2"
        ).get(
            user=self.user,
            poll=self.poll_videos,
            entity_1__uid=data["entity_a"]["uid"],
            entity_2__uid=data["entity_b"]["uid"],
        )
        comparisons_nbr = Comparison.objects.filter(user=self.user).count()

        # check the database integrity
        self.assertEqual(comparisons_nbr, initial_comparisons_nbr + 1)

        # do not check the response data as the `test_authenticated_can_create`
        # method already tests it
        self.assertEqual(comparison.poll, self.poll_videos)
        self.assertEqual(comparison.user, self.user)
        self.assertEqual(comparison.entity_1.uid, data["entity_a"]["uid"])
        self.assertEqual(comparison.entity_2.uid, data["entity_b"]["uid"])
        self.assertEqual(comparison.duration_ms, data["duration_ms"])

    def test_authenticated_cant_create_invalid_uid(self):
        """
        An authenticated user can't create a comparison with an unknown
        uid namespace, or invalid YouTube id.
        """
        self.client.force_authenticate(user=self.user)

        # use an invalid uid namespace
        data = deepcopy(self.non_existing_comparison)
        data["entity_a"]["uid"] = data["entity_a"]["uid"].replace("yt:", "invalid:")

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # use an invalid YouTube id
        data = deepcopy(self.non_existing_comparison)
        data["entity_a"]["uid"] = "yt:abc"

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_cant_create_criteria_scores_without_mandatory(self):
        """
        An authenticated user can't create a new comparison without explicitly
        providing a `creteria` and a `score` field for each criterion.

        Only required fields of the comparison's criteria are tested.
        """
        initial_comparisons_nbr = Comparison.objects.filter(user=self.user).count()

        data = deepcopy(self.non_existing_comparison)
        data["criteria_scores"][0].pop("score")

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )
        comparisons_nbr = Comparison.objects.filter(user=self.user).count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(comparisons_nbr, initial_comparisons_nbr)

        data = deepcopy(self.non_existing_comparison)
        data["criteria_scores"][0].pop("criteria")

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )
        comparisons_nbr = Comparison.objects.filter(user=self.user).count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(comparisons_nbr, initial_comparisons_nbr)

    def test_missing_non_optional_criteria_in_comparison(self):
        self.client.force_authenticate(self.user)
        data = deepcopy(self.non_existing_comparison)
        data["criteria_scores"][0]["criteria"] = "pedagogy"
        response = self.client.post(self.comparisons_base_url, data, format="json")
        self.assertContains(
            response,
            "Missing required criteria",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    def test_authenticated_cant_create_twice(self):
        """
        An authenticated user can't create two comparisons for the same couple
        of videos.
        """
        data = deepcopy(self.non_existing_comparison)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_cant_create_reverse(self):
        """
        An authenticated user can't create two comparisons for the same couple
        of videos, even by providing the video id in the reverse order.
        """
        initial_comparisons_nbr = Comparison.objects.all().count()
        data = deepcopy(self.non_existing_comparison)

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # swap the uid
        data["entity_a"]["uid"], data["entity_b"]["uid"] = (
            data["entity_b"]["uid"],
            data["entity_a"]["uid"],
        )

        response = self.client.post(
            self.comparisons_base_url,
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # the database must contain exactly one more comparison, not two
        self.assertEqual(
            Comparison.objects.all().count(),
            initial_comparisons_nbr + 1,
        )

    def test_anonymous_cant_list(self):
        """
        An anonymous user can't list its comparisons.
        """
        response = self.client.get(
            self.comparisons_base_url,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_cant_list_non_existing_poll(self):
        """
        An authenticated user can't list its comparisons in a non-existing
        poll.
        """
        self.client.force_authenticate(user=self.user)
        non_existing_poll = "non-existing"

        response = self.client.get(
            "/users/me/comparisons/{}/".format(non_existing_poll),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_can_list(self):
        """
        An authenticated user can list its comparisons.
        """
        comparisons_made = Comparison.objects.filter(user=self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            self.comparisons_base_url,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], comparisons_made.count())
        self.assertEqual(len(response.data["results"]), comparisons_made.count())

        # the comparisons must be ordered by datetime_lastedit
        results = response.data["results"]
        comp1 = results[0]
        comp2 = results[1]

        self.assertEqual(comp1["entity_a"]["uid"], self.comparisons[1].entity_1.uid)
        self.assertEqual(comp1["entity_b"]["uid"], self.comparisons[1].entity_2.uid)
        self.assertEqual(comp1["duration_ms"], self.comparisons[1].duration_ms)

        self.assertEqual(comp2["entity_a"]["uid"], self.comparisons[0].entity_1.uid)
        self.assertEqual(comp2["entity_b"]["uid"], self.comparisons[0].entity_2.uid)

        self.assertEqual(len(comp1["entity_a_contexts"]), 1)
        self.assertEqual(comp1["entity_a_contexts"][0]["text"], self.ent_context_01_text.text)
        self.assertEqual(comp1["entity_b_contexts"], [])
        self.assertEqual(comp2["duration_ms"], self.comparisons[0].duration_ms)

    def test_authenticated_can_list_filtered(self):
        """
        An authenticated user can list its comparisons filtered by a video id.
        """
        comparisons_made = Comparison.objects.filter(
            Q(entity_1__uid=self._uid_02) | Q(entity_2__uid=self._uid_02),
            poll=self.poll_videos,
            user=self.user,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            "{}/{}/".format(self.comparisons_base_url, self._uid_02),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], comparisons_made.count())
        self.assertEqual(len(response.data["results"]), comparisons_made.count())

        # currently the GET API returns an unordered list, so the assertions
        # are made unordered too
        for comparison in response.data["results"]:
            if comparison["entity_a"]["uid"] != self._uid_02:
                self.assertEqual(comparison["entity_b"]["uid"], self._uid_02)

            self.assertEqual(comparison["duration_ms"], 102)

    def test_anonymous_cant_read(self):
        """
        An anonymous user can't read one of its comparisons.
        """
        response = self.client.get(
            "{}/{}/{}/".format(self.comparisons_base_url, self._uid_01, self._uid_02),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_cant_read_non_existing_poll(self):
        """
        An authenticated user can't read one of its comparisons in a
        non-existing poll.
        """
        self.client.force_authenticate(user=self.user)
        non_existing_poll = "non-existing"

        response = self.client.get(
            "/users/me/comparisons/{}/{}/{}/".format(
                non_existing_poll, self._uid_01, self._uid_02
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_can_read(self):
        """
        An authenticated user can read one of its comparisons.

        The `entity_a` and  `entity_b` fields in the response must respectively
        match the positional arguments of the URL requested.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            "{}/{}/{}/".format(self.comparisons_base_url, self._uid_01, self._uid_02),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["entity_a"]["uid"], self._uid_01)
        self.assertEqual(data["entity_b"]["uid"], self._uid_02)
        self.assertEqual(len(data["entity_a_contexts"]), 1)
        self.assertEqual(data["entity_a_contexts"][0]["text"], self.ent_context_01_text.text)
        self.assertEqual(data["entity_b_contexts"], [])
        self.assertEqual(data["duration_ms"], 102)

    def test_authenticated_can_read_reverse(self):
        """
        An authenticated user can read one of its comparisons, even if the
        video id are reversed in the URL requested.

        The `entity_a` and  `entity_b` fields in the response must respectively
        match the positional arguments of the URL requested.
        """
        self.client.force_authenticate(user=self.user)

        # assert the comparison 02 / 01 does not exist in this order in the
        # database, in order to test the GET view with reversed parameters
        with self.assertRaises(ObjectDoesNotExist):
            Comparison.objects.get(
                poll=self.poll_videos,
                user=self.user,
                entity_1__uid=self._uid_02,
                entity_2__uid=self._uid_01,
            )

        response = self.client.get(
            "{}/{}/{}/".format(
                self.comparisons_base_url,
                self._uid_02,
                self._uid_01,
            ),
            format="json",
        )

        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["entity_a"]["uid"], self._uid_02)
        self.assertEqual(data["entity_b"]["uid"], self._uid_01)
        self.assertEqual(data["entity_a_contexts"], [])
        self.assertEqual(len(data["entity_b_contexts"]), 1)
        self.assertEqual(data["entity_b_contexts"][0]["text"], self.ent_context_01_text.text)
        self.assertEqual(data["duration_ms"], 102)

    def test_anonymous_cant_update(self):
        """
        An anonymous user can't update a comparison.
        """
        response = self.client.put(
            "{}/{}/{}/".format(
                self.comparisons_base_url,
                self._uid_01,
                self._uid_02,
            ),
            {"criteria_scores": [{"criteria": "largely_recommended", "score": 10, "weight": 10}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_cant_update_non_existing_poll(self):
        """
        An authenticated user can't update a comparison in a non-existing poll.
        """
        self.client.force_authenticate(user=self.user)
        non_existing_poll = "non-existing"

        response = self.client.put(
            "/users/me/comparisons/{}/{}/{}/".format(
                non_existing_poll, self._uid_01, self._uid_02
            ),
            {"criteria_scores": [{"criteria": "largely_recommended", "score": 10, "weight": 10}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_can_update(self):
        self.client.force_authenticate(user=self.user)

        ent_context = EntityContext.objects.create(
            name="context_safe_03",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.videos[2].metadata["video_id"]},
            unsafe=False,
            enabled=True,
            poll=self.poll_videos,
        )

        ent_context_text = EntityContextLocale.objects.create(
            context=ent_context,
            language="en",
            text="Hello context 03",
        )

        comparison1 = Comparison.objects.create(
            poll=self.poll_videos,
            user=self.user,
            entity_1=self.videos[2],
            entity_2=self.videos[3],
        )
        comparison2 = Comparison.objects.create(
            poll=self.poll_videos,
            user=self.user,
            entity_1=self.videos[1],
            entity_2=self.videos[2],
        )
        response = self.client.put(
            "{}/{}/{}/".format(
                self.comparisons_base_url,
                self._uid_03,
                self._uid_04,
            ),
            {"criteria_scores": [{"criteria": "largely_recommended", "score": 10, "weight": 10}]},
            format="json",
        )

        data = response.data
        self.assertEqual(len(data["entity_a_contexts"]), 1)
        self.assertEqual(data["entity_a_contexts"][0]["text"], ent_context_text.text)
        self.assertEqual(data["entity_b_contexts"], [])

        response = self.client.get(
            self.comparisons_base_url,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comp1 = response.data["results"][0]
        comp2 = response.data["results"][1]
        self.assertEqual(comp1["entity_a"]["uid"], comparison1.entity_1.uid)
        self.assertEqual(comp1["entity_b"]["uid"], comparison1.entity_2.uid)
        self.assertEqual(comp2["entity_a"]["uid"], comparison2.entity_1.uid)
        self.assertEqual(comp2["entity_b"]["uid"], comparison2.entity_2.uid)

    def test_anonymous_cant_delete(self):
        """
        An anonymous user can't delete a comparison.
        """
        # ensure ObjectDoesNoteExist is not raised
        Comparison.objects.get(
            poll=self.poll_videos,
            user=self.user,
            entity_1=self.videos[0],
            entity_2=self.videos[1],
        )

        response = self.client.delete(
            "{}/{}/{}/".format(
                self.comparisons_base_url,
                self._uid_01,
                self._uid_02,
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # ensure ObjectDoesNoteExist is still not raised
        Comparison.objects.get(
            poll=self.poll_videos,
            user=self.user,
            entity_1=self.videos[0],
            entity_2=self.videos[1],
        )

    def test_authenticated_cant_delete_non_existing_poll(self):
        """
        An authenticated user can't delete a comparison in a non-existing
        poll.
        """
        self.client.force_authenticate(user=self.user)
        non_existing_poll = "non-existing"

        response = self.client.delete(
            "/users/me/comparisons/{}/{}/{}/".format(
                non_existing_poll, self._uid_01, self._uid_02
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_can_delete(self):
        """
        An authenticated user can delete a comparison.
        """
        self.client.force_authenticate(user=self.user)

        # ensure ObjectDoesNoteExist is not raised
        Comparison.objects.get(
            poll=self.poll_videos,
            user=self.user,
            entity_1=self.videos[0],
            entity_2=self.videos[1],
        )

        response = self.client.delete(
            "{}/{}/{}/".format(
                self.comparisons_base_url,
                self._uid_01,
                self._uid_02,
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(ObjectDoesNotExist):
            Comparison.objects.get(
                poll=self.poll_videos,
                user=self.user,
                entity_1=self.videos[0],
                entity_2=self.videos[1],
            )

    def test_n_ratings_from_video(self):
        self.client.force_authenticate(user=self.user)

        VideoFactory(metadata__video_id=self._uid_05.split(":")[1])
        VideoFactory(metadata__video_id=self._uid_06.split(":")[1])
        VideoFactory(metadata__video_id=self._uid_07.split(":")[1])

        data1 = {
            "entity_a": {"uid": self._uid_05},
            "entity_b": {"uid": self._uid_06},
            "criteria_scores": [{"criteria": "largely_recommended", "score": 10, "weight": 10}],
            "duration_ms": 103,
        }
        response = self.client.post(
            self.comparisons_base_url,
            data1,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data2 = {
            "entity_a": {"uid": self._uid_05},
            "entity_b": {"uid": self._uid_07},
            "criteria_scores": [{"criteria": "largely_recommended", "score": 10, "weight": 10}],
            "duration_ms": 103,
        }
        response = self.client.post(
            self.comparisons_base_url,
            data2,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.other)

        data3 = {
            "entity_a": {"uid": self._uid_05},
            "entity_b": {"uid": self._uid_06},
            "criteria_scores": [{"criteria": "largely_recommended", "score": 10, "weight": 10}],
            "duration_ms": 103,
        }
        response = self.client.post(
            self.comparisons_base_url,
            data3,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        video5 = Entity.objects.get(uid=self._uid_05)
        video6 = Entity.objects.get(uid=self._uid_06)
        video7 = Entity.objects.get(uid=self._uid_07)

        self.assertEqual(video5.all_poll_ratings.get().n_contributors, 2)
        self.assertEqual(video5.all_poll_ratings.get().n_comparisons, 3)
        self.assertEqual(video6.all_poll_ratings.get().n_contributors, 2)
        self.assertEqual(video6.all_poll_ratings.get().n_comparisons, 2)
        self.assertEqual(video7.all_poll_ratings.get().n_contributors, 1)
        self.assertEqual(video7.all_poll_ratings.get().n_comparisons, 1)

    @patch("tournesol.utils.api_youtube.get_video_metadata")
    def test_metadata_refresh_on_comparison_creation(self, mock_get_video_metadata):
        mock_get_video_metadata.return_value = {"views": "42000"}

        user = UserFactory(username="non_existing_user")
        self.client.force_authenticate(user=user)

        video01, video02, video03 = self.videos[:3]
        video01.last_metadata_request_at = None
        video01.save()
        video02.last_metadata_request_at = time_ago(days=7)
        video02.save()
        video03.last_metadata_request_at = timezone.now()
        video03.save()

        data = {
            "entity_a": {"uid": self._uid_01},
            "entity_b": {"uid": self._uid_02},
            "criteria_scores": [{"criteria": "largely_recommended", "score": 10, "weight": 10}],
        }
        response = self.client.post(self.comparisons_base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        self.assertEqual(len(mock_get_video_metadata.mock_calls), 2)
        video01.refresh_from_db()
        self.assertEqual(video01.metadata["views"], 42000)

        data = {
            "entity_a": {"uid": self._uid_01},
            "entity_b": {"uid": self._uid_03},
            "criteria_scores": [{"criteria": "largely_recommended", "score": 10, "weight": 10}],
        }

        response = self.client.post(self.comparisons_base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        # Video01 has been refreshed and video03 was already up-to-date.
        # No additional call to YouTube API should be visible.
        self.assertEqual(len(mock_get_video_metadata.mock_calls), 2)

    def test_invalid_criteria_in_comparison(self):
        self.client.force_authenticate(self.user)
        data = deepcopy(self.non_existing_comparison)
        data["criteria_scores"][0]["criteria"] = "invalid"
        response = self.client.post(self.comparisons_base_url, data, format="json")
        self.assertContains(
            response, "not a valid criteria", status_code=status.HTTP_400_BAD_REQUEST
        )

    def test_comparing_removes_from_rate_later(self):
        """
        A video compared several times should be removed from the user's
        rate-later list.

        If the user hasn't configured `rate_later__auto_remove`, the video
        should be removed after 4 comparisons.
        """

        # [GIVEN] a user with no settings configured.
        self.user.settings = {}
        self.user.save(update_fields=["settings"])

        self.client.force_authenticate(user=self.user)
        video_main, *videos = (VideoFactory() for _ in range(5))

        data = {"entity": {"uid": video_main.uid}}
        self.client.post(
            f"/users/me/rate_later/{self.poll_videos.name}/",
            data,
            format="json",
        )

        # The main video should be in the rate later list after 1 comparison.
        self._compare(video_main.uid, videos[0].uid)
        self.assertEqual(RateLater.objects.filter(entity=video_main).count(), 1)

        # The main video should not be in the rate later list after 4 comparison.
        for video in videos[1:]:
            self._compare(video_main.uid, video.uid)
        self.assertEqual(RateLater.objects.filter(entity=video_main).count(), 0)


class ComparisonWithMehestanTest(TransactionTestCase):
    def setUp(self):
        self.poll = PollFactory(algorithm=ALGORITHM_MEHESTAN)
        CriteriaRankFactory(poll=self.poll, criteria__name="criteria1")
        CriteriaRankFactory(poll=self.poll, criteria__name="criteria2", optional=True)

        self.entities = VideoFactory.create_batch(3)
        self.user1, self.user2 = UserFactory.create_batch(2)

        comparison = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[0],
            entity_2=self.entities[1],
        )

        for (criteria, score) in [("criteria1", 1), ("criteria2", 2)]:
            ComparisonCriteriaScoreFactory(
                comparison=comparison,
                criteria=criteria,
                score=score,
            )

        self.client = APIClient()

    @override_settings(
        UPDATE_MEHESTAN_SCORES_ON_COMPARISON=True,
        MEHESTAN_MULTIPROCESSING=False,
    )
    def test_update_individual_scores_after_new_comparison(self):
        call_command("ml_train")

        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 4)
        self.assertEqual(EntityCriteriaScore.objects.filter(score_mode="default").count(), 4)

        # user2 has no contributor scores before the comparison is submitted
        self.assertEqual(
            ContributorRatingCriteriaScore.objects
            .filter(contributor_rating__user=self.user2)
            .count(),
            0
        )

        self.client.force_authenticate(self.user2)
        resp = self.client.post(
            f"/users/me/comparisons/{self.poll.name}",
            data={
                "entity_a": {"uid": self.entities[0].uid},
                "entity_b": {"uid": self.entities[2].uid},
                "criteria_scores": [{"criteria": "criteria1", "score": 3}],
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 201, resp.content)

        # Individual scores related to the new comparison have been computed
        self.assertEqual(
            ContributorRatingCriteriaScore.objects
            .filter(contributor_rating__user=self.user2)
            .count(),
            2
        )
        # The score related to the less prefered entity is negative
        user_score = ContributorRatingCriteriaScore.objects.get(
            contributor_rating__user=self.user2,
            contributor_rating__entity=self.entities[0],
            criteria="criteria1",
        )
        self.assertLess(user_score.score, 0)

        # Global scores and individual scores related to other users are unchanged
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 6)
        self.assertEqual(EntityCriteriaScore.objects.filter(score_mode="default").count(), 4)


class ComparisonApiWithInactivePoll(TestCase):
    def setUp(self):
        self.poll = PollFactory(active=False)
        self.user = UserFactory()
        self.videos = [
            VideoFactory(),
            VideoFactory(),
        ]
        ComparisonFactory(
            user=self.user,
            poll=self.poll,
            entity_1=self.videos[0],
            entity_2=self.videos[1],
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_user_can_list_comparisons(self):
        resp = self.client.get(f"/users/me/comparisons/{self.poll.name}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), 1)

    def test_user_can_get_existing_comparison(self):
        resp = self.client.get(
            f"/users/me/comparisons/{self.poll.name}/{self.videos[0].uid}/{self.videos[1].uid}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["entity_a"]["uid"], self.videos[0].uid)

    def test_user_cannot_create_comparison(self):
        resp = self.client.post(f"/users/me/comparisons/{self.poll.name}", data={
            "entity_a": {
                "uid": "uid1"
            },
            "entity_b": {
                "uid": "uid2"
            },
            "criteria_scores": [],
        }, format="json")
        self.assertContains(
            resp, "inactive poll", status_code=status.HTTP_403_FORBIDDEN
        )

    def test_user_cannot_update_comparison(self):
        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.videos[0].uid}/{self.videos[1].uid}/",
            data={
                "criteria_scores": []
            },
            format="json"
        )
        self.assertContains(
            resp, "inactive poll", status_code=status.HTTP_403_FORBIDDEN
        )

    def test_user_cannot_delete_comparison(self):
        resp = self.client.delete(
            f"/users/me/comparisons/{self.poll.name}/{self.videos[0].uid}/{self.videos[1].uid}/")
        self.assertContains(
            resp, "inactive poll", status_code=status.HTTP_403_FORBIDDEN
        )
