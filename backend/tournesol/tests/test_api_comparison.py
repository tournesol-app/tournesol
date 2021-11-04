from copy import deepcopy
import datetime

from django.db.models import ObjectDoesNotExist, Q
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from ..models import Video, Comparison


class ComparisonApiTestCase(TestCase):
    """
    TestCase of the comparison API.

    For each endpoint, the test case checks:
        - authorizations
        - permissions
        - behaviour
    """

    _user = "username"
    _user2 = "username2"
    _other = "other_username"

    _video_id_01 = "video_id_01"
    _video_id_02 = "video_id_02"
    _video_id_03 = "video_id_03"
    _video_id_04 = "video_id_04"
    _video_id_05 = "video_id_05"
    _video_id_06 = "video_id_06"
    _video_id_07 = "video_id_07"

    non_existing_comparison = {
        "video_a": {
            "video_id": _video_id_01
        },
        "video_b": {
            "video_id": _video_id_03
        },
        "criteria_scores": [
            {
                "criteria": "over_the_top",
                "score": 10,
                "weight": 10
            }
        ],
        "duration_ms": 103
    }

    def setUp(self):
        """
        Set-up a minimal set of data to test the ComparisonList API.

        At least 4 videos and 2 users with 2 comparisons each are required.
        """
        user = User.objects.create(username=self._user)
        user2 = User.objects.create(username=self._user2)
        other = User.objects.create(username=self._other)
        now = datetime.datetime.now()

        self.videos = Video.objects.bulk_create([
            Video(video_id=self._video_id_01, name=self._video_id_01),
            Video(video_id=self._video_id_02, name=self._video_id_02),
            Video(video_id=self._video_id_03, name=self._video_id_03),
            Video(video_id=self._video_id_04, name=self._video_id_04)
        ])

        self.comparisons = Comparison.objects.bulk_create([
            # "user" will have the comparisons: 01 / 02 and 01 / 04
            Comparison(
                user=user, video_1=self.videos[0], video_2=self.videos[1],
                duration_ms=102,
                datetime_lastedit=now,
            ),
            Comparison(
                user=user, video_1=self.videos[0], video_2=self.videos[3],
                duration_ms=104,
                datetime_lastedit=now + datetime.timedelta(minutes=1),
            ),
            # "other" will have the comparisons: 03 / 02 and 03 / 04
            Comparison(
                user=other, video_1=self.videos[2], video_2=self.videos[1],
                duration_ms=302,
                datetime_lastedit=now + datetime.timedelta(minutes=3),
            ),
            Comparison(
                user=other, video_1=self.videos[2], video_2=self.videos[3],
                duration_ms=304,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
        ])

    def _remove_optional_fields(self, comparison):
        comparison.pop("duration_ms", None)

        if "criteria_scores" in comparison:
            for criteria_score in comparison["criteria_scores"]:
                criteria_score.pop("weight", None)

        return comparison

    def test_anonymous_cant_create(self):
        """
        An anonymous user can't create a comparison.
        """
        client = APIClient()
        initial_comparisons_nbr = Comparison.objects.all().count()
        data = deepcopy(self.non_existing_comparison)

        response = client.post(
            reverse("tournesol:comparisons_me_list"), data, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        comparisons = Comparison.objects.filter(
            video_1__video_id=self._video_id_01,
            video_2__video_id=self._video_id_03
        )
        self.assertFalse(comparisons.exists())

        comparisons = Comparison.objects.filter(
            video_1__video_id=self._video_id_03,
            video_2__video_id=self._video_id_01
        )
        self.assertFalse(comparisons.exists())
        self.assertEqual(
            Comparison.objects.all().count(),
            initial_comparisons_nbr
        )

    def test_authenticated_can_create(self):
        """
        An authenticated user can create a new comparison.

        Ensure the database object contains the data sent.

        Also ensure the object representation included in the API response
        contains the data sent.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        initial_comparisons_nbr = Comparison.objects.filter(user=user).count()
        data = deepcopy(self.non_existing_comparison)

        client.force_authenticate(user=user)

        response = client.post(
            reverse("tournesol:comparisons_me_list"), data, format="json",
        )

        comparison = Comparison.objects.select_related("user", "video_1", "video_2").get(
            user=user,
            video_1__video_id=data["video_a"]["video_id"],
            video_2__video_id=data["video_b"]["video_id"],
        )
        comparisons_nbr = Comparison.objects.filter(user=user).count()

        # check the authorization
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check the database integrity
        self.assertEqual(comparisons_nbr,
                         initial_comparisons_nbr + 1)

        self.assertEqual(comparison.user, user)
        self.assertEqual(comparison.video_1.video_id,
                         data["video_a"]["video_id"])
        self.assertEqual(comparison.video_2.video_id,
                         data["video_b"]["video_id"])
        self.assertEqual(comparison.duration_ms, data["duration_ms"])

        comparison_criteria_scores = comparison.criteria_scores.all()
        self.assertEqual(comparison_criteria_scores.count(),
                         len(data["criteria_scores"]))
        self.assertEqual(comparison_criteria_scores[0].criteria,
                         data["criteria_scores"][0]["criteria"])
        self.assertEqual(comparison_criteria_scores[0].score,
                         data["criteria_scores"][0]["score"])
        self.assertEqual(comparison_criteria_scores[0].weight,
                         data["criteria_scores"][0]["weight"])

        # check the representation integrity
        self.assertEqual(response.data["video_a"]["video_id"],
                         data["video_a"]["video_id"])
        self.assertEqual(response.data["video_b"]["video_id"],
                         data["video_b"]["video_id"])
        self.assertEqual(response.data["duration_ms"],
                         data["duration_ms"])

        self.assertEqual(len(response.data["criteria_scores"]),
                         len(data["criteria_scores"]))
        self.assertEqual(response.data["criteria_scores"][0]["criteria"],
                         data["criteria_scores"][0]["criteria"])
        self.assertEqual(response.data["criteria_scores"][0]["score"],
                         data["criteria_scores"][0]["score"])
        self.assertEqual(response.data["criteria_scores"][0]["weight"],
                         data["criteria_scores"][0]["weight"])

    def test_authenticated_can_create_without_optional(self):
        """
        An authenticated user can create a new comparison with only required
        fields.

        All optional fields of the comparison and its related criteria are
        tested.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        initial_comparisons_nbr = Comparison.objects.filter(user=user).count()
        data = self._remove_optional_fields(deepcopy(self.non_existing_comparison))

        client.force_authenticate(user=user)

        response = client.post(
            reverse("tournesol:comparisons_me_list"), data, format="json",
        )

        comparison = Comparison.objects.select_related("user", "video_1", "video_2").get(
            user=user,
            video_1__video_id=data["video_a"]["video_id"],
            video_2__video_id=data["video_b"]["video_id"],
        )
        comparisons_nbr = Comparison.objects.filter(user=user).count()

        # check the authorization
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check the database integrity (only the criteria scores part)
        self.assertEqual(comparisons_nbr,
                         initial_comparisons_nbr + 1)

        self.assertEqual(comparison.duration_ms,
                         Comparison._meta.get_field("duration_ms").get_default())

        comparison_criteria_scores = comparison.criteria_scores.all()
        self.assertEqual(comparison_criteria_scores.count(),
                         len(data["criteria_scores"]))
        self.assertEqual(comparison_criteria_scores[0].weight, 1)

    def test_authenticated_cant_create_criteria_scores_without_mandatory(self):
        """
        An authenticated user can't create a new comparison without explicitly
        providing a `creteria` and a `score` field for each criterion.

        Only required fields of the comparison's criteria are tested.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        initial_comparisons_nbr = Comparison.objects.filter(user=user).count()

        data = deepcopy(self.non_existing_comparison)
        data["criteria_scores"][0].pop("score")

        client.force_authenticate(user=user)

        response = client.post(
            reverse("tournesol:comparisons_me_list"), data, format="json",
        )
        comparisons_nbr = Comparison.objects.filter(user=user).count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(comparisons_nbr, initial_comparisons_nbr)

        data = deepcopy(self.non_existing_comparison)
        data["criteria_scores"][0].pop("criteria")

        response = client.post(
            reverse("tournesol:comparisons_me_list"), data, format="json",
        )
        comparisons_nbr = Comparison.objects.filter(user=user).count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(comparisons_nbr, initial_comparisons_nbr)

    def test_authenticated_cant_create_twice(self):
        """
        An authenticated user can't create two comparisons for the same couple
        of videos.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        data = deepcopy(self.non_existing_comparison)

        client.force_authenticate(user=user)

        response = client.post(
            reverse("tournesol:comparisons_me_list"), data, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = client.post(
            reverse("tournesol:comparisons_me_list"), data, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_cant_create_reverse(self):
        """
        An authenticated user can't create two comparisons for the same couple
        of videos, even by providing the video id in the reverse order.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        initial_comparisons_nbr = Comparison.objects.all().count()
        data = deepcopy(self.non_existing_comparison)

        client.force_authenticate(user=user)

        response = client.post(
            reverse("tournesol:comparisons_me_list"), data, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # swap the video id
        data['video_a']['video_id'], data['video_b']['video_id'] = \
            data['video_b']['video_id'], data['video_a']['video_id']

        response = client.post(
            reverse("tournesol:comparisons_me_list"), data, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # the database must contain exactly one more comparison, not two
        self.assertEqual(Comparison.objects.all().count(),
                         initial_comparisons_nbr + 1)

    def test_anonymous_cant_list(self):
        """
        An anonymous user can't list its comparisons.
        """
        client = APIClient()

        response = client.get(
            reverse("tournesol:comparisons_me_list"), format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_list(self):
        """
        An authenticated user can list its comparisons.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        comparisons_made = Comparison.objects.filter(user=user)

        client.force_authenticate(user=user)

        response = client.get(
            reverse("tournesol:comparisons_me_list"), format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], comparisons_made.count())
        self.assertEqual(len(response.data["results"]), comparisons_made.count())

        # the comparisons must be ordered by datetime_lastedit
        comparison1 = response.data["results"][0]
        comparison2 = response.data["results"][1]

        self.assertEqual(comparison1["video_a"]["video_id"],
                         self.comparisons[1].video_1.video_id)
        self.assertEqual(comparison1["video_b"]["video_id"],
                         self.comparisons[1].video_2.video_id)
        self.assertEqual(comparison1["duration_ms"],
                         self.comparisons[1].duration_ms)

        self.assertEqual(comparison2["video_a"]["video_id"],
                         self.comparisons[0].video_1.video_id)
        self.assertEqual(comparison2["video_b"]["video_id"],
                         self.comparisons[0].video_2.video_id)
        self.assertEqual(comparison2["duration_ms"],
                         self.comparisons[0].duration_ms)

    def test_authenticated_can_list_filtered(self):
        """
        An authenticated user can list its comparisons filtered by a video id.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        comparisons_made = Comparison.objects.filter(
            Q(video_1__video_id=self._video_id_02) |
            Q(video_2__video_id=self._video_id_02),
            user=user
        )

        client.force_authenticate(user=user)

        response = client.get(
            reverse("tournesol:comparisons_me_list_filtered", args=[
                self._video_id_02
            ]), format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], comparisons_made.count())
        self.assertEqual(len(response.data["results"]), comparisons_made.count())

        # currently the GET API returns an unordered list, so the assertions
        # are made unordered too
        for comparison in response.data["results"]:
            if comparison["video_a"]["video_id"] != self._video_id_02:
                self.assertEqual(comparison["video_b"]["video_id"], self._video_id_02)

            self.assertEqual(comparison["duration_ms"], 102)

    def test_anonymous_cant_read(self):
        """
        An anonymous user can't read one of its comparisons.
        """
        client = APIClient()

        response = client.get(
            reverse("tournesol:comparisons_me_detail", args=[
                self._video_id_01, self._video_id_02
            ]), format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_read(self):
        """
        An authenticated user can read one of its comparisons.

        The `video_a` and  `video_b` fields in the response must respectively
        match the positional arguments of the URL requested.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)

        client.force_authenticate(user=user)

        response = client.get(
            reverse("tournesol:comparisons_me_detail", args=[
                self._video_id_01, self._video_id_02
            ]), format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["video_a"]["video_id"],
                         self._video_id_01)
        self.assertEqual(response.data["video_b"]["video_id"],
                         self._video_id_02)
        self.assertEqual(response.data["duration_ms"], 102)

    def test_authenticated_can_read_reverse(self):
        """
        An authenticated user can read one of its comparisons, even if the
        video id are reversed in the URL requested.

        The `video_a` and  `video_b` fields in the response must respectively
        match the positional arguments of the URL requested.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        client.force_authenticate(user=user)

        # assert the comparison 02 / 01 does not exist in this order in the
        # database, in order to test the GET view with reversed parameters
        with self.assertRaises(ObjectDoesNotExist):
            Comparison.objects.get(
                user=user,
                video_1__video_id=self._video_id_02,
                video_2__video_id=self._video_id_01
            )

        response = client.get(
            reverse("tournesol:comparisons_me_detail", args=[
                self._video_id_02, self._video_id_01,
            ]), format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["video_a"]["video_id"],
                         self._video_id_02)
        self.assertEqual(response.data["video_b"]["video_id"],
                         self._video_id_01)
        self.assertEqual(response.data["duration_ms"], 102)

    def test_authenticated_integrated_comparison_list(self):
        client = APIClient()

        user = User.objects.get(username=self._user)
        client.force_authenticate(user=user)
        comparison1 = Comparison.objects.create(
            user=user,
            video_1=self.videos[2],
            video_2=self.videos[3],
        )
        comparison2 = Comparison.objects.create(
            user=user,
            video_1=self.videos[1],
            video_2=self.videos[2],
        )
        client.put(
            reverse(
                "tournesol:comparisons_me_detail",
                args=[self._video_id_03, self._video_id_04]
            ),
            {
                'criteria_scores': [
                    {
                        "criteria": "over_the_top",
                        "score": 10,
                        "weight": 10
                    }
                ]
            },
            format="json",
        )
        response = client.get(
            reverse("tournesol:comparisons_me_list"), format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result_comparison1 = response.data["results"][0]
        result_comparison2 = response.data["results"][1]
        self.assertEqual(result_comparison1["video_a"]["video_id"], comparison1.video_1.video_id)
        self.assertEqual(result_comparison1["video_b"]["video_id"], comparison1.video_2.video_id)
        self.assertEqual(result_comparison2["video_a"]["video_id"], comparison2.video_1.video_id)
        self.assertEqual(result_comparison2["video_b"]["video_id"], comparison2.video_2.video_id)

    def test_n_ratings_from_video(self):
        client = APIClient()

        user = User.objects.get(username=self._user)
        client.force_authenticate(user=user)
        Video.objects.create(video_id=self._video_id_05)
        Video.objects.create(video_id=self._video_id_06)
        Video.objects.create(video_id=self._video_id_07)
        data1 = {
            "video_a": {
                "video_id": self._video_id_05
            },
            "video_b": {
                "video_id": self._video_id_06
            },
            "criteria_scores": [
                {
                    "criteria": "over_the_top",
                    "score": 10,
                    "weight": 10
                }
            ],
            "duration_ms": 103
        }
        response = client.post(
            reverse("tournesol:comparisons_me_list"), data1, format="json",
        )
        self.assertEqual(response.status_code, 201)

        data2 = {
            "video_a": {
                "video_id": self._video_id_05
            },
            "video_b": {
                "video_id": self._video_id_07
            },
            "criteria_scores": [
                {
                    "criteria": "over_the_top",
                    "score": 10,
                    "weight": 10
                }
            ],
            "duration_ms": 103
        }
        response = client.post(
            reverse("tournesol:comparisons_me_list"), data2, format="json",
        )
        self.assertEqual(response.status_code, 201)

        user2 = User.objects.get(username=self._user2)
        client.force_authenticate(user=user2)

        data3 = {
            "video_a": {
                "video_id": self._video_id_05
            },
            "video_b": {
                "video_id": self._video_id_06
            },
            "criteria_scores": [
                {
                    "criteria": "over_the_top",
                    "score": 10,
                    "weight": 10
                }
            ],
            "duration_ms": 103
        }
        response = client.post(
            reverse("tournesol:comparisons_me_list"), data3, format="json",
        )
        self.assertEqual(response.status_code, 201)

        video5 = Video.objects.get(video_id=self._video_id_05)
        video6 = Video.objects.get(video_id=self._video_id_06)
        video7 = Video.objects.get(video_id=self._video_id_07)

        self.assertEqual(video5.rating_n_contributors, 2)
        self.assertEqual(video5.rating_n_ratings, 3)
        self.assertEqual(video6.rating_n_contributors, 2)
        self.assertEqual(video6.rating_n_ratings, 2)
        self.assertEqual(video7.rating_n_contributors, 1)
        self.assertEqual(video7.rating_n_ratings, 1)
