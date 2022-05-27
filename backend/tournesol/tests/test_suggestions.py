import datetime

from django.test import TestCase
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models import Poll
from tournesol.suggestions.graph import Graph
from tournesol.suggestions.suggester_store import _SuggesterStore
from tournesol.suggestions.suggestionprovider import SuggestionProvider
from tournesol.tests.factories.comparison import ComparisonCriteriaScoreFactory, ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.entity_score import EntityCriteriaScoreFactory
from tournesol.tests.factories.ratings import (
    ContributorRatingCriteriaScoreFactory,
    ContributorRatingFactory,
)
from tournesol.tests.factories.scaling import ContributorScalingFactory


class SuggestionAPITestCase(TestCase):
    # users available in the test
    _user = "username"
    _other = "other_username"
    _central_scaled_user = "central_user"

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
        self.central_scaled_user = UserFactory(username=self._central_scaled_user, is_staff=True)
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

        # Populate the rating table - is already done ?
        for i, v in enumerate(self.videos[5:]):
            contributor_rating = ContributorRatingFactory(
                poll__name=self.poll.name,
                entity=v,
                user=self.other,
                is_public=True,
            )
            ContributorRatingCriteriaScoreFactory(
                contributor_rating=contributor_rating,
                criteria=self._criteria,
                score=0,
            )
        for i, v in enumerate(self.videos[:5]):
            contributor_rating = ContributorRatingFactory(
                poll=self.poll,
                entity=v,
                user=self.user,
                is_public=True,
            )
            ContributorRatingCriteriaScoreFactory(
                contributor_rating=contributor_rating,
                criteria=self._criteria,
                score=2.2,
            )
        for i, v in enumerate(self.videos[:3]):
            contributor_rating = ContributorRatingFactory(
                poll=self.poll,
                entity=v,
                user=self.central_scaled_user,
                is_public=True,
            )
            ContributorRatingCriteriaScoreFactory(
                contributor_rating=contributor_rating,
                criteria=self._criteria,
                score=0.125,
            )
        for i, v in enumerate(self.videos[7:]):
            contributor_rating = ContributorRatingFactory(
                poll=self.poll,
                entity=v,
                user=self.central_scaled_user,
                is_public=True,
            )
            ContributorRatingCriteriaScoreFactory(
                contributor_rating=contributor_rating,
                criteria=self._criteria,
                score=0.25,
            )

        # Populate the comparison table
        self.comparisons = [
            # "user" will have comparisons for elements 2 by 2 for videos 0 to 4, the video
            # 0 is compared to all the other and no other comparison has been performed
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
                duration_ms=105,
                datetime_lastedit=now + datetime.timedelta(minutes=1),
            ),
            ComparisonFactory(
                user=self.user,
                entity_1=self.videos[0],
                entity_2=self.videos[3],
                duration_ms=108,
                datetime_lastedit=now + datetime.timedelta(minutes=1),
            ),
            ComparisonFactory(
                user=self.user,
                entity_1=self.videos[0],
                entity_2=self.videos[4],
                duration_ms=111,
                datetime_lastedit=now + datetime.timedelta(minutes=1),
            ),
            # "other" will have comparisons for elements 2 by 2 for videos 5 to 9, each time only
            #             # the video to the next and then the last video to the first
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
                duration_ms=306,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[8],
                entity_2=self.videos[9],
                duration_ms=308,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[5],
                entity_2=self.videos[9],
                duration_ms=310,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
            # "central" user also has some comparisons, but not that much
            ComparisonFactory(
                user=self.central_scaled_user,
                entity_1=self.videos[0],
                entity_2=self.videos[9],
                duration_ms=201,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
            ComparisonFactory(
                user=self.central_scaled_user,
                entity_1=self.videos[0],
                entity_2=self.videos[1],
                duration_ms=202,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
            ComparisonFactory(
                user=self.central_scaled_user,
                entity_1=self.videos[8],
                entity_2=self.videos[9],
                duration_ms=203,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
            ComparisonFactory(
                user=self.central_scaled_user,
                entity_1=self.videos[1],
                entity_2=self.videos[8],
                duration_ms=204,
                datetime_lastedit=now + datetime.timedelta(minutes=2),
            ),
            ComparisonFactory(
                user=self.central_scaled_user,
                entity_1=self.videos[2],
                entity_2=self.videos[7],
                duration_ms=205,
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
        # Populate the scaling table
        ContributorScalingFactory(
            user=self.user,
            poll=self.poll,
            criteria=self._criteria,
            scale_uncertainty=0.75,
            translation_uncertainty=0.25,
        )
        ContributorScalingFactory(
            user=self.other,
            poll=self.poll,
            criteria=self._criteria,
            scale_uncertainty=1,
            translation_uncertainty=0.5,
        )
        ContributorScalingFactory(
            user=self.central_scaled_user,
            poll=self.poll,
            criteria=self._criteria,
            scale_uncertainty=0,
            translation_uncertainty=0.0,
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_class_instantiation(self):
        local_poll = self.poll
        Graph(self.user, local_poll, self._criteria)
        actual_store = _SuggesterStore()
        actual_store.get_suggester(self.poll)

    def test_algo_gives_right_number_vid(self):
        suggester = SuggestionProvider(self.poll)
        videos = suggester.get_first_video_recommendation(self.user, 3)
        assert len(videos) == 3
        snd_videos = suggester.get_second_video_recommendation(self.user, videos[0].uid, 3)
        assert len(snd_videos) == 3

    def test_complete_graph_construction(self):
        suggester = SuggestionProvider(self.poll)
        assert len(suggester._complete_graph.edges) == len(self.comparisons)
        assert len(suggester._complete_graph.nodes) == len(self.videos)

    def test_lazy_loading(self):
        suggester = SuggestionProvider(self.poll)
        assert self.user.id not in suggester._user_specific_graphs.keys()
        suggester.get_first_video_recommendation(self.user, 6)
        assert self.user.id in suggester._user_specific_graphs.keys()

# This would be nice to test, but this property is not easy to compute...
    def test_most_informative_vid_given_first(self):
        suggester = SuggestionProvider(self.poll)
        user_videos = suggester.get_first_video_recommendation(self.central_scaled_user, 6)
        last_vid_score = 1000
        for v in user_videos:
            assert v.video1_score <= last_vid_score
            last_vid_score = v.video1_score

        user2_videos = suggester.get_second_video_recommendation(
            self.central_scaled_user,
            user_videos[0].uid,
            6
        )
        last_vid_score = 1000
        for v in user2_videos:
            assert v.video2_score[user_videos[0]] <= last_vid_score
            last_vid_score = v.video2_score[user_videos[0]]

    def test_suggestions_personalization(self):
        suggester = SuggestionProvider(self.poll)
        user_videos = suggester.get_first_video_recommendation(self.user, 6)
        other_videos = suggester.get_first_video_recommendation(self.other, 6)
        all_the_same = True
        for v1, v2 in zip(user_videos, other_videos):
            if v1 != v2:
                all_the_same = False
        assert not all_the_same

        all_the_same = True
        user_second_videos_a = suggester.get_second_video_recommendation(
            self.central_scaled_user,
            user_videos[0].uid,
            8
        )
        user_second_videos_b = suggester.get_second_video_recommendation(
            self.central_scaled_user,
            user_videos[-1].uid,
            8
        )
        for v1, v2 in zip(user_second_videos_a, user_second_videos_b):
            if v1 != v2:
                all_the_same = False
        assert not all_the_same
