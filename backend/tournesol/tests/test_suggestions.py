import datetime

import numpy as np
from django.test import TestCase
from rest_framework.test import APIClient

from core.models.user import EmailDomain
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
    _user_no_comparison = "absent"
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
        self.user_no_comparison = UserFactory(username=self._user_no_comparison)
        self.other = UserFactory(username=self._other)
        EmailDomain.objects.create(
            domain="@trusted.test", status=EmailDomain.STATUS_ACCEPTED
        )
        self.central_scaled_user = UserFactory(
            username=self._central_scaled_user,
            email="staff@trusted.test",
            is_staff=True
        )
        self.sparsity_comparison_user = UserFactory(
            username="SparseUser",
            email="spared@trusted.test",
            is_staff=True
        )

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
        for v in self.videos:
            contributor_rating = ContributorRatingFactory(
                poll=self.poll,
                entity=v,
                user=self.sparsity_comparison_user,
                is_public=True,
            )
            ContributorRatingCriteriaScoreFactory(
                contributor_rating=contributor_rating,
                criteria=self._criteria,
                score=0,
            )
        contributor_rating = ContributorRatingFactory(
            poll=self.poll,
            entity=self.videos[4],
            user=self.user_no_comparison,
            is_public=True,
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=contributor_rating,
            criteria=self._criteria,
            score=0,
        )
        contributor_rating = ContributorRatingFactory(
            poll=self.poll,
            entity=self.videos[6],
            user=self.user_no_comparison,
            is_public=True,
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=contributor_rating,
            criteria=self._criteria,
            score=0,
        )

        # Populate the comparison table
        self.comparisons = [
            # "user" will have comparisons for elements 2 by 2 for videos 0 to 4, the video
            # 0 is compared to all the other and no other comparison has been performed
            ComparisonFactory(
                user=self.user,
                entity_1=self.videos[0],
                entity_2=self.videos[1],
            ),
            ComparisonFactory(
                user=self.user,
                entity_1=self.videos[0],
                entity_2=self.videos[2],
            ),
            ComparisonFactory(
                user=self.user,
                entity_1=self.videos[0],
                entity_2=self.videos[3],
            ),
            ComparisonFactory(
                user=self.user,
                entity_1=self.videos[0],
                entity_2=self.videos[4],
            ),
            # "other" will have comparisons for elements 2 by 2 for videos 5 to 9, each time only
            #             # the video to the next and then the last video to the first
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[5],
                entity_2=self.videos[6],
            ),
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[6],
                entity_2=self.videos[7],
            ),
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[7],
                entity_2=self.videos[8],
            ),
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[8],
                entity_2=self.videos[9],
            ),
            ComparisonFactory(
                user=self.other,
                entity_1=self.videos[5],
                entity_2=self.videos[9],
            ),
            # "central" user also has some comparisons, but not that much
            ComparisonFactory(
                user=self.central_scaled_user,
                entity_1=self.videos[0],
                entity_2=self.videos[9],
            ),
            ComparisonFactory(
                user=self.central_scaled_user,
                entity_1=self.videos[0],
                entity_2=self.videos[1],
            ),
            ComparisonFactory(
                user=self.central_scaled_user,
                entity_1=self.videos[8],
                entity_2=self.videos[9],
            ),
            ComparisonFactory(
                user=self.central_scaled_user,
                entity_1=self.videos[1],
                entity_2=self.videos[8],
            ),
            ComparisonFactory(
                user=self.central_scaled_user,
                entity_1=self.videos[2],
                entity_2=self.videos[7],
            ),
            ComparisonFactory(
                user=self.user_no_comparison,
                entity_1=self.videos[4],
                entity_2=self.videos[6],
            ),
        ]

        # Here we created a comparison graph very dense between all the videos but two
        for i, va in enumerate(self.videos[2:]):
            for j, vb in enumerate(self.videos[i+3:]):
                self.comparisons.append(ComparisonFactory(
                    user=self.sparsity_comparison_user,
                    entity_1=va,
                    entity_2=vb,
                ))

        # We then link the last nodes by only one link
        self.comparisons.append(ComparisonFactory(
            user=self.sparsity_comparison_user,
            entity_1=self.videos[1],
            entity_2=self.videos[4],
        ))
        # We then link the last node by only one link
        self.comparisons.append(ComparisonFactory(
            user=self.sparsity_comparison_user,
            entity_1=self.videos[0],
            entity_2=self.videos[1],
        ))

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

    def test_absent_user_does_not_crash(self):
        suggester = SuggestionProvider(self.poll)
        vid = suggester.get_first_video_recommendation(self.user_no_comparison, 6)
        suggester.get_second_video_recommendation(self.user_no_comparison, vid[0].uid, 6)

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
            v_score = v.score_computation(user_videos[0])
            assert v_score <= last_vid_score
            last_vid_score = v_score

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

    def test_suggestions_for_new_user(self):
        new_user = UserFactory()
        suggester = SuggestionProvider(self.poll)

        suggestions = suggester.get_first_video_recommendation(new_user, 6)
        assert len(suggestions) == 6

        suggestions = suggester.get_second_video_recommendation(new_user, self.videos[9].uid, 6)
        assert len(suggestions) == 6

    def test_sparsification_metric(self):
        suggester = SuggestionProvider(self.poll)
        suggester.get_first_video_recommendation(self.sparsity_comparison_user, 6)
        user_graph = suggester._user_specific_graphs[self.sparsity_comparison_user.id]

        assert np.linalg.eigvalsh(user_graph.normalized_adjacency_matrix)[-1] - 1 < 10e-8

        for n in user_graph.nodes:
            if n.uid == self.videos[0].uid:
                alone_node = n
            elif n.uid == self.videos[1].uid:
                bridge_node = n

        for n in user_graph.nodes:
            if n != bridge_node and n != alone_node:
                max_value = n.graph_sparsity(alone_node)
                bridge_value = n.graph_sparsity(bridge_node)
                assert bridge_value < max_value
                base_value = -1
                for m in user_graph.nodes:
                    if n == m:
                        continue
                    if base_value == -1 and m not in {bridge_node, alone_node}:
                        base_value = n.graph_sparsity(m)
                        assert base_value <= bridge_value
                    if m == alone_node:
                        assert n.graph_sparsity(m) == max_value
                    elif m == bridge_node:
                        assert n.graph_sparsity(m) == bridge_value
                    else:
                        assert n.graph_sparsity(m) == base_value

    def test_similarity_bounded_value(self):
        suggester = SuggestionProvider(self.poll)
        suggester.get_first_video_recommendation(self.sparsity_comparison_user, 6)
        user_graph = suggester._user_specific_graphs[self.sparsity_comparison_user.id]

        for n in user_graph.nodes:
            for m in user_graph.nodes:
                assert n.score_computation(m) <= 2

    def test_suggestions_with_new_videos(self):
        new_video = VideoFactory()
        ComparisonCriteriaScoreFactory(
            comparison__user=self.central_scaled_user,
            comparison__entity_1=new_video,
            comparison__entity_2=self.videos[0],
            criteria=self._criteria,
        )
        suggester = SuggestionProvider(self.poll)
        new_comparison = ComparisonCriteriaScoreFactory(
            comparison__user=self.central_scaled_user,
            comparison__entity_2=self.videos[0],
            criteria=self._criteria,
        )

        suggestions = suggester.get_first_video_recommendation(self.central_scaled_user, 6)
        assert len(suggestions) == 6

        suggestions = suggester.get_second_video_recommendation(self.central_scaled_user, self.videos[0].uid, 6)
        assert len(suggestions) == 6
