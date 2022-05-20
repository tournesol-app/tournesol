import datetime

from django.test import TestCase
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models import (
    Comparison,
    ContributorRatingCriteriaScore,
    Entity,
    EntityCriteriaScore,
    Poll,
)
from tournesol.suggestions.graph import Graph
from tournesol.suggestions.suggester_store import SuggesterStore
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.entity_score import EntityCriteriaScoreFactory
from tournesol.tests.factories.comparison import ComparisonCriteriaScoreFactory
from tournesol.tests.factories.ratings import ContributorRatingCriteriaScoreFactory, ContributorRatingFactory
from tournesol.tests.factories.scaling import ContributorScalingFactory


class SuggestionAPITestCase(TestCase):
    # users available in the test
    _user = "username"
    _other = "other_username"

    # videos available in all tests
    _uid_00 = "yt:video_id_00"
    _uid_01 = "yt:video_id_01"
    _uid_02 = "yt:video_id_02"
    _uid_03 = "yt:video_id_03"
    _uid_04 = "yt:video_id_04"
    _uid_05 = "yt:video_id_05"
    _uid_06 = "yt:video_id_06"
    _uid_07 = "yt:video_id_07"
    _uid_08 = "yt:video_id_08"
    _uid_09 = "yt:video_id_09"

    # non-existing videos that can be created
    _uid_10 = "yt:video_id_10"
    _uid_11 = "yt:video_id_11"

    _criteria = "largely_recommended"

    def setUp(self):
        """
        Set up a minimal set of data to test the suggestion API.

        At least 4 videos and 2 users with 2 comparisons each are required.
        """
        self.poll = Poll.default_poll()
        self.comparisons_base_url = "/users/me/comparisons/{}".format(
            self.poll.name
        )

        self.client = APIClient()

        # Populate the user table
        self.user = UserFactory(username=self._user)
        self.other = UserFactory(username=self._other)
        now = datetime.datetime.now()

        # Populate the video table
        self.videos = [
            VideoFactory(metadata__video_id=self._uid_00.split(":")[1]),
            VideoFactory(metadata__video_id=self._uid_01.split(":")[1]),
            VideoFactory(metadata__video_id=self._uid_02.split(":")[1]),
            VideoFactory(metadata__video_id=self._uid_03.split(":")[1]),
            VideoFactory(metadata__video_id=self._uid_04.split(":")[1]),
            VideoFactory(metadata__video_id=self._uid_05.split(":")[1]),
            VideoFactory(metadata__video_id=self._uid_06.split(":")[1]),
            VideoFactory(metadata__video_id=self._uid_07.split(":")[1]),
            VideoFactory(metadata__video_id=self._uid_08.split(":")[1]),
            VideoFactory(metadata__video_id=self._uid_09.split(":")[1]),
        ]

        # Populate the comparison table
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
                entity_2=self.videos[2],
                duration_ms=104,
                datetime_lastedit=now + datetime.timedelta(minutes=1),
            ),
            ComparisonFactory(
                user=self.user,
                entity_1=self.videos[0],
                entity_2=self.videos[3],
                duration_ms=104,
                datetime_lastedit=now + datetime.timedelta(minutes=1),
            ),
            ComparisonFactory(
                user=self.user,
                entity_1=self.videos[0],
                entity_2=self.videos[4],
                duration_ms=104,
                datetime_lastedit=now + datetime.timedelta(minutes=1),
            ),
            # "other" will have the comparisons: 03 / 02 and 03 / 04
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[5],
                entity_2=self.videos[6],
                duration_ms=302,
                datetime_lastedit=now + datetime.timedelta(minutes=3),
            ),
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[6],
                entity_2=self.videos[7],
                duration_ms=304,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[7],
                entity_2=self.videos[8],
                duration_ms=304,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[8],
                entity_2=self.videos[9],
                duration_ms=304,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[5],
                entity_2=self.videos[9],
                duration_ms=306,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
        ]

        # CriteriaRankFactory(poll=self.poll, criteria__name="largely_recommended")
        # Populate the ComparisonCriteriaScore table
        for c in self.comparisons:
            ComparisonCriteriaScoreFactory(
                comparison=c,
                criteria=self._criteria,
                score=4,
            )
        # Populate the EntityCriteriaScore table
        for i, v in enumerate(self.videos):
            EntityCriteriaScoreFactory(
                entity=v,
                poll=self.poll,
                criteria=self._criteria,
                score=i,
                uncertainty=i/2,
            )
        # Populate the rating table - is already done ?
        # for i, v in enumerate(self.videos[:5]):
        #     contributor_rating = ContributorRatingFactory(
        #         poll=self.poll,
        #         entity=v,
        #         user=self.other,
        #         is_public=True,
        #     )
        #     ContributorRatingCriteriaScoreFactory(
        #         contributor_rating=contributor_rating,
        #         criteria=self._criteria,
        #         score=i,
        #     )
        # for i, v in enumerate(self.videos[5:]):
        #     contributor_rating = ContributorRatingFactory(
        #         poll=self.poll,
        #         entity=v,
        #         user=self.user,
        #         is_public=True,
        #     )
        #     ContributorRatingCriteriaScoreFactory(
        #         contributor_rating=contributor_rating,
        #         criteria=self._criteria,
        #         score=i,
        #     )

        # Populate the scaling table
        ContributorScalingFactory(
            user=self.user,
            poll=self.poll,
            scale_uncertainty=0.75,
            translation_uncertainty=0.25,
        )
        ContributorScalingFactory(
            user=self.other,
            poll=self.poll,
            scale_uncertainty=1,
            translation_uncertainty=0.5,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_class_instantiation(self):
        self.client.force_authenticate(user=self.user)
        local_poll = self.poll
        Graph(None, local_poll, self._criteria)
        SuggesterStore.actual_store.get_suggester(local_poll)

    def test_algo_gives_right_number_vids(self):
        pass

    def test_graph_construction(self):
        pass

    def test_lazy_loading(self):
        pass

    def test_most_informative_vid_given_first(self):
        pass

    def test_suggestions_personalization(self):
        pass
