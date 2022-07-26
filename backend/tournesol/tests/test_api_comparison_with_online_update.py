from unittest.mock import patch

from django.core.management import call_command
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from core.utils.time import time_ago
from tournesol.models import ContributorRatingCriteriaScore, EntityCriteriaScore
from tournesol.models.poll import ALGORITHM_MEHESTAN
from tournesol.tests.factories.comparison import ComparisonCriteriaScoreFactory, ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.poll import CriteriaRankFactory, PollFactory


class ComparisonWithOnlineHeuristicMehestanTest(TransactionTestCase):
    def setUp(self):
        self.poll = PollFactory(algorithm=ALGORITHM_MEHESTAN)
        CriteriaRankFactory(poll=self.poll, criteria__name="criteria1")

        self.entities = VideoFactory.create_batch(2)
        (
            self.user1,
            self.user2,
            self.user3,
            self.user4,
            self.user5,
        ) = UserFactory.create_batch(5)

        comparison_user1 = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[0],
            entity_2=self.entities[1],
        )
        comparison_user2 = ComparisonFactory(
            poll=self.poll,
            user=self.user2,
            entity_1=self.entities[0],
            entity_2=self.entities[1],
        )
        comparison_user3 = ComparisonFactory(
            poll=self.poll,
            user=self.user3,
            entity_1=self.entities[0],
            entity_2=self.entities[1],
        )
        comparison_user4 = ComparisonFactory(
            poll=self.poll,
            user=self.user4,
            entity_1=self.entities[0],
            entity_2=self.entities[1],
        )
        comparisons = list()
        comparisons.append((comparison_user1, 10))
        comparisons.append((comparison_user2, 10))
        comparisons.append((comparison_user3, -10))
        comparisons.append((comparison_user4, -10))

        for (comparison, score) in comparisons:
            ComparisonCriteriaScoreFactory(
                comparison=comparison,
                criteria="criteria1",
                score=score,
            )

        self.client = APIClient()

    # @override_settings(UPDATE_MEHESTAN_SCORES_ON_COMPARISON=True)
    # def test_insert_individual_scores_after_new_comparison_with_online_heuristic_update(
    #     self,
    # ):
    #     call_command("ml_train")
    #     contrib_before_insert = set(
    #         ContributorRatingCriteriaScore.objects.all().values_list()
    #     )
    #     self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 8)
    #     self.assertEqual(
    #         EntityCriteriaScore.objects.filter(score_mode="default").count(), 2
    #     )

    #     # user5 has no contributor scores before the comparison is submitted
    #     self.assertEqual(
    #         ContributorRatingCriteriaScore.objects.filter(
    #             contributor_rating__user=self.user5
    #         ).count(),
    #         0,
    #     )
    #     self.client.force_authenticate(self.user5)
    #     resp = self.client.post(
    #         f"/users/me/comparisons/{self.poll.name}",
    #         data={
    #             "entity_a": {"uid": self.entities[0].uid},
    #             "entity_b": {"uid": self.entities[1].uid},
    #             "criteria_scores": [{"criteria": "criteria1", "score": 2}],
    #         },
    #         format="json",
    #     )

    #     self.assertEqual(resp.status_code, 201, resp.content)

    #     # Individual scores related to the new comparison have been computed
    #     self.assertEqual(
    #         ContributorRatingCriteriaScore.objects.filter(
    #             contributor_rating__user=self.user5
    #         ).count(),
    #         2,
    #     )
    #     # The score related to the less prefered entity is negative
    #     user_score = ContributorRatingCriteriaScore.objects.get(
    #         contributor_rating__user=self.user5,
    #         contributor_rating__entity=self.entities[0],
    #         criteria="criteria1",
    #     )
    #     self.assertLess(user_score.score, 0)

    #     contrib_after_insert = set(
    #         ContributorRatingCriteriaScore.objects.all().values_list()
    #     )

    #     diff_insert = contrib_after_insert.difference(contrib_before_insert)
    #     # have 2 new contributorRatingCriteria and have the same old contributorRatingCriteria
    #     self.assertEqual(len(diff_insert), 2)
    #     self.assertEqual(len(contrib_before_insert.difference(contrib_after_insert)), 0)
    #     # new individual scores 8+2=10
    #     self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 10)
    #     # no new global scores = 2
    #     self.assertEqual(
    #         EntityCriteriaScore.objects.filter(score_mode="default").count(), 2
    #     )

    # @override_settings(UPDATE_MEHESTAN_SCORES_ON_COMPARISON=True)
    # def test_update_individual_scores_after_new_comparison_with_online_heuristic_update(
    #     self,
    # ):
    #     call_command("ml_train")
    #     contrib_before_update = set(
    #         ContributorRatingCriteriaScore.objects.all().values_list()
    #     )
    #     self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 8)
    #     self.assertEqual(
    #         EntityCriteriaScore.objects.filter(score_mode="default").count(), 2
    #     )

    #     self.client.force_authenticate(self.user4)
    #     resp = self.client.put(
    #         f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[1].uid}/",
    #         data={
    #             "criteria_scores": [{"criteria": "criteria1", "score": 10}],
    #         },
    #         format="json",
    #     )

    #     self.assertEqual(resp.status_code, 200, resp.content)

    #     # Individual scores related to the new comparison have been computed
    #     self.assertEqual(
    #         ContributorRatingCriteriaScore.objects.filter(
    #             contributor_rating__user=self.user4
    #         ).count(),
    #         2,
    #     )
    #     # The score related to the less prefered entity is negative
    #     user_score = ContributorRatingCriteriaScore.objects.get(
    #         contributor_rating__user=self.user4,
    #         contributor_rating__entity=self.entities[0],
    #         criteria="criteria1",
    #     )
    #     self.assertLess(user_score.score, 0)

    #     contrib_after_update = set(
    #         ContributorRatingCriteriaScore.objects.all().values_list()
    #     )

    #     diff_update = contrib_after_update.difference(contrib_before_update)
    #     # the update has generate two differences
    #     self.assertEqual(len(diff_update), 2)
    #     self.assertEqual(len(contrib_before_update.difference(contrib_after_update)), 2)
    #     # no new individual scores 8+0=8
    #     self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 8)
    #     # no new global scores = 2
    #     self.assertEqual(
    #         EntityCriteriaScore.objects.filter(score_mode="default").count(), 2
    #     )

    # @override_settings(UPDATE_MEHESTAN_SCORES_ON_COMPARISON=True)
    # def test_delete_individual_scores_after_new_comparison_with_online_heuristic_update(
    #     self,
    # ):
    #     call_command("ml_train")
    #     contrib_before_update = set(
    #         ContributorRatingCriteriaScore.objects.all().values_list()
    #     )
    #     self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 8)
    #     self.assertEqual(
    #         EntityCriteriaScore.objects.filter(score_mode="default").count(), 2
    #     )

    #     self.client.force_authenticate(self.user4)
    #     resp = self.client.delete(
    #         f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[1].uid}/",
    #     )

    #     self.assertEqual(resp.status_code, 204, resp.content)

    #     # WIP : to fix
    #     self.assertEqual(
    #         ContributorRatingCriteriaScore.objects.filter(
    #             contributor_rating__user=self.user4
    #         ).count(),
    #         2,
    #     )
    #     # The score related to the less prefered entity is negative
    #     user_score = ContributorRatingCriteriaScore.objects.get(
    #         contributor_rating__user=self.user4,
    #         contributor_rating__entity=self.entities[0],
    #         criteria="criteria1",
    #     )
    #     self.assertLess(user_score.score, 200)

    #     contrib_after_update = set(
    #         ContributorRatingCriteriaScore.objects.all().values_list()
    #     )

    #     diff_update = contrib_after_update.difference(contrib_before_update)
    #     # the update has generate two differences
    #     self.assertEqual(len(diff_update), 0)
    #     self.assertEqual(len(contrib_before_update.difference(contrib_after_update)), 0)
    #     # no new individual scores 8+0=8
    #     self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 8)
    #     # no new global scores = 2
    #     self.assertEqual(
    #         EntityCriteriaScore.objects.filter(score_mode="default").count(), 2
    #     )


class AdvancedComparisonWithOnlineHeuristicMehestanTest(TransactionTestCase):
    def setUp(self):
        self.poll = PollFactory(algorithm=ALGORITHM_MEHESTAN)
        CriteriaRankFactory(poll=self.poll, criteria__name="criteria1")

        self.entities = VideoFactory.create_batch(5)
        (
            self.user1,
            self.user2,
        ) = UserFactory.create_batch(2)

        comparison_user1_1 = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[0],
            entity_2=self.entities[1],
        )
        comparison_user1_2 = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[1],
            entity_2=self.entities[2],
        )
        comparison_user1_3 = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[0],
            entity_2=self.entities[2],
        )
        comparison_user1_4 = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[0],
            entity_2=self.entities[3],
        )
        comparison_user1_5 = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[0],
            entity_2=self.entities[4],
        )
        comparison_user2 = ComparisonFactory(
            poll=self.poll,
            user=self.user2,
            entity_1=self.entities[0],
            entity_2=self.entities[1],
        )
        comparisons = list()
        comparisons.append((comparison_user1_1, 10))
        comparisons.append((comparison_user1_2, 10))
        comparisons.append((comparison_user1_3, 10))
        comparisons.append((comparison_user1_4, 10))
        comparisons.append((comparison_user1_5, 10))
        comparisons.append((comparison_user2, 10))

        for (comparison, score) in comparisons:
            ComparisonCriteriaScoreFactory(
                comparison=comparison,
                criteria="criteria1",
                score=score,
            )

        self.client = APIClient()

    @override_settings(UPDATE_MEHESTAN_SCORES_ON_COMPARISON=True)
    def test_insert_all_individual_scores_with_online_heuristic_update(
        self,
    ):
        call_command("ml_train")

        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 7)
        self.assertEqual(
            EntityCriteriaScore.objects.filter(score_mode="default").count(), 5
        )

        self.client.force_authenticate(self.user2)
        resp = self.client.post(
            f"/users/me/comparisons/{self.poll.name}",
            data={
                "entity_a": {"uid": self.entities[1].uid},
                "entity_b": {"uid": self.entities[2].uid},
                "criteria_scores": [{"criteria": "criteria1", "score": 10}],
            },
            format="json",
        )
        call_command("ml_train")

        return 
        self.assertEqual(resp.status_code, 201, resp.content)
        resp = self.client.post(
            f"/users/me/comparisons/{self.poll.name}",
            data={
                "entity_a": {"uid": self.entities[2].uid},
                "entity_b": {"uid": self.entities[3].uid},
                "criteria_scores": [{"criteria": "criteria1", "score": 10}],
            },
            format="json",
        )

        # call_command("ml_train")
        self.assertEqual(resp.status_code, 201, resp.content)
        resp = self.client.post(
            f"/users/me/comparisons/{self.poll.name}",
            data={
                "entity_a": {"uid": self.entities[3].uid},
                "entity_b": {"uid": self.entities[4].uid},
                "criteria_scores": [{"criteria": "criteria1", "score": 10}],
            },
            format="json",
        )

        # call_command("ml_train")
        self.assertEqual(resp.status_code, 201, resp.content)
        resp = self.client.post(
            f"/users/me/comparisons/{self.poll.name}",
            data={
                "entity_a": {"uid": self.entities[4].uid},
                "entity_b": {"uid": self.entities[0].uid},
                "criteria_scores": [{"criteria": "criteria1", "score": 10}],
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 201, resp.content)
        call_command("ml_train")

    @override_settings(UPDATE_MEHESTAN_SCORES_ON_COMPARISON=True)
    def test_delete_all_individual_scores_with_online_heuristic_update(
        self,
    ):
        call_command("ml_train")

        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 7)
        self.assertEqual(
            EntityCriteriaScore.objects.filter(score_mode="default").count(), 5
        )

        self.client.force_authenticate(self.user1)
        resp = self.client.delete(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[1].uid}/",
        )

        self.assertEqual(resp.status_code, 204, resp.content)
        resp = self.client.delete(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[2].uid}/",
        )

        self.assertEqual(resp.status_code, 204, resp.content)
        resp = self.client.delete(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[3].uid}/",
        )

        self.assertEqual(resp.status_code, 204, resp.content)
        resp = self.client.delete(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[4].uid}/",
        )

        self.assertEqual(resp.status_code, 204, resp.content)
        resp = self.client.delete(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[1].uid}/{self.entities[2].uid}/",
        )

        self.assertEqual(resp.status_code, 204, resp.content)
        # 5 indiv score with 0.0 score
        self.assertEqual(
            ContributorRatingCriteriaScore.objects.filter(
                contributor_rating__user=self.user1
            ).count(),
            5,
        )
        for (
            contributorRatingCriteriaScore
        ) in ContributorRatingCriteriaScore.objects.filter(
            contributor_rating__user=self.user1
        ).all():
            self.assertEqual(contributorRatingCriteriaScore.score, 0.0)

        # # no new global scores = 5
        self.assertEqual(
            EntityCriteriaScore.objects.filter(score_mode="default").count(), 5
        )

    @override_settings(UPDATE_MEHESTAN_SCORES_ON_COMPARISON=True)
    def test_update_all_individual_scores_with_online_heuristic_update(
        self,
    ):
        call_command("ml_train")

        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 7)
        self.assertEqual(
            EntityCriteriaScore.objects.filter(score_mode="default").count(), 5
        )

        self.client.force_authenticate(self.user1)
        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[1].uid}/",
            data={
                "criteria_scores": [{"criteria": "criteria1", "score": 0}],
            },
            format="json",
        )
        call_command("ml_train")
        self.assertEqual(resp.status_code, 200, resp.content)
        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[2].uid}/",
            data={
                "criteria_scores": [{"criteria": "criteria1", "score": 0}],
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 200, resp.content)

        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[3].uid}/",
            data={
                "criteria_scores": [{"criteria": "criteria1", "score": 0}],
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 200, resp.content)
        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[4].uid}/",
            data={
                "criteria_scores": [{"criteria": "criteria1", "score": 0}],
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 200, resp.content)

        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[1].uid}/{self.entities[2].uid}/",
            data={
                "criteria_scores": [{"criteria": "criteria1", "score": 0}],
            },
            format="json",
        )
        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[1].uid}/{self.entities[2].uid}/",
            data={
                "criteria_scores": [{"criteria": "criteria1", "score": 0}],
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 200, resp.content)
        # 5 indiv score with 0.0 score
        self.assertEqual(
            ContributorRatingCriteriaScore.objects.filter(
                contributor_rating__user=self.user1
            ).count(),
            5,
        )

        # no new global scores = 5
        self.assertEqual(
            EntityCriteriaScore.objects.filter(score_mode="default").count(), 5
        )


class ExpertComparisonWithOnlineHeuristicMehestanTest(TransactionTestCase):
    def setUp(self):
        self.poll = PollFactory(algorithm=ALGORITHM_MEHESTAN)
        CriteriaRankFactory(poll=self.poll, criteria__name="criteria1")

        self.entities = VideoFactory.create_batch(5)
        (
            self.user1,
            self.user2,
        ) = UserFactory.create_batch(2)

        comparison_user1_1 = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[0],
            entity_2=self.entities[1],
        )
        comparison_user1_2 = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[1],
            entity_2=self.entities[2],
        )
        comparison_user1_3 = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[2],
            entity_2=self.entities[3],
        )
        comparison_user1_4 = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[3],
            entity_2=self.entities[4],
        )
        comparison_user1_5 = ComparisonFactory(
            poll=self.poll,
            user=self.user1,
            entity_1=self.entities[4],
            entity_2=self.entities[0],
        )
        comparison_user2 = ComparisonFactory(
            poll=self.poll,
            user=self.user2,
            entity_1=self.entities[0],
            entity_2=self.entities[1],
        )
        comparisons = list()
        comparisons.append((comparison_user1_1, 10))
        comparisons.append((comparison_user1_2, 10))
        comparisons.append((comparison_user1_3, 10))
        comparisons.append((comparison_user1_4, 10))
        comparisons.append((comparison_user1_5, 10))
        comparisons.append((comparison_user2, 10))

        for (comparison, score) in comparisons:
            ComparisonCriteriaScoreFactory(
                comparison=comparison,
                criteria="criteria1",
                score=score,
            )

        self.client = APIClient()

    @override_settings(UPDATE_MEHESTAN_SCORES_ON_COMPARISON=True)
    def test_delete_all_individual_scores_with_online_heuristic_update(
        self,
    ):
        call_command("ml_train")

        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 7)
        self.assertEqual(
            EntityCriteriaScore.objects.filter(score_mode="default").count(), 5
        )

        self.client.force_authenticate(self.user1)
        resp = self.client.delete(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[1].uid}/",
        )

        self.assertEqual(resp.status_code, 204, resp.content)
        resp = self.client.delete(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[1].uid}/{self.entities[2].uid}/",
        )

        self.assertEqual(resp.status_code, 204, resp.content)
        resp = self.client.delete(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[2].uid}/{self.entities[3].uid}/",
        )

        self.assertEqual(resp.status_code, 204, resp.content)
        resp = self.client.delete(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[3].uid}/{self.entities[4].uid}/",
        )

        self.assertEqual(resp.status_code, 204, resp.content)
        resp = self.client.delete(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[4].uid}/{self.entities[0].uid}/",
        )

        self.assertEqual(resp.status_code, 204, resp.content)
        # 5 indiv score with 0.0 score
        self.assertEqual(
            ContributorRatingCriteriaScore.objects.filter(
                contributor_rating__user=self.user1
            ).count(),
            5,
        )
        for (
            contributorRatingCriteriaScore
        ) in ContributorRatingCriteriaScore.objects.filter(
            contributor_rating__user=self.user1
        ).all():
            self.assertEqual(contributorRatingCriteriaScore.score, 0.0)

        # # no new global scores = 5
        self.assertEqual(
            EntityCriteriaScore.objects.filter(score_mode="default").count(), 5
        )

    @override_settings(UPDATE_MEHESTAN_SCORES_ON_COMPARISON=True)
    def test_update_all_individual_scores_with_online_heuristic_update(
        self,
    ):
        call_command("ml_train")

        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 7)
        self.assertEqual(
            EntityCriteriaScore.objects.filter(score_mode="default").count(), 5
        )

        self.client.force_authenticate(self.user1)
        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[0].uid}/{self.entities[1].uid}/",
            data={
                "criteria_scores": [{"criteria": "criteria1", "score": 0}],
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 200, resp.content)
        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[1].uid}/{self.entities[2].uid}/",
            data={
                "criteria_scores": [{"criteria": "criteria1", "score": 0}],
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 200, resp.content)

        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[2].uid}/{self.entities[3].uid}/",
            data={
                "criteria_scores": [{"criteria": "criteria1", "score": 0}],
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 200, resp.content)
        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[3].uid}/{self.entities[4].uid}/",
            data={
                "criteria_scores": [{"criteria": "criteria1", "score": 0}],
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 200, resp.content)

        resp = self.client.put(
            f"/users/me/comparisons/{self.poll.name}/{self.entities[4].uid}/{self.entities[0].uid}/",
            data={
                "criteria_scores": [{"criteria": "criteria1", "score": 0}],
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 200, resp.content)
        # 5 indiv score with 0.0 score
        self.assertEqual(
            ContributorRatingCriteriaScore.objects.filter(
                contributor_rating__user=self.user1
            ).count(),
            5,
        )

        # no new global scores = 5
        self.assertEqual(
            EntityCriteriaScore.objects.filter(score_mode="default").count(), 5
        )


# class MyriadOfComparisonWithOnlineHeuristicMehestanTest(TransactionTestCase):
#     def setUp(self):
#         self.poll = PollFactory(algorithm=ALGORITHM_MEHESTAN)
#         CriteriaRankFactory(poll=self.poll, criteria__name="criteria1")

#         self.number_entities = 100
#         self.entities = VideoFactory.create_batch(self.number_entities)
#         (
#             self.user1,
#             self.user2,
#         ) = UserFactory.create_batch(2)

#         comparisons = [
#             (
#                 ComparisonFactory(
#                     poll=self.poll,
#                     user=self.user1,
#                     entity_1=self.entities[i],
#                     entity_2=self.entities[j],
#                 ),
#                 10,
#             )
#             for i in range(self.number_entities)
#             for j in range(i + 1, self.number_entities)
#         ]

#         for (comparison, score) in comparisons:
#             ComparisonCriteriaScoreFactory(
#                 comparison=comparison,
#                 criteria="criteria1",
#                 score=score,
#             )

#         self.client = APIClient()

#     @override_settings(UPDATE_MEHESTAN_SCORES_ON_COMPARISON=True)
#     @patch("tournesol.throttling.BurstUserRateThrottle.get_rate")
#     @patch("tournesol.throttling.SustainedUserRateThrottle.get_rate")
#     def test_delete_all_individual_scores_with_online_heuristic_update(self, mock1,mock2):
#         mock1.return_value = "10000/min"
#         mock2.return_value = "360000/hour"
#         call_command("ml_train")

#         self.assertEqual(
#             ContributorRatingCriteriaScore.objects.count(), self.number_entities
#         )
#         self.assertEqual(
#             EntityCriteriaScore.objects.filter(score_mode="default").count(),
#             self.number_entities,
#         )

#         self.client.force_authenticate(self.user1)

#         for i in range(self.number_entities):
#             for j in range(i + 1, self.number_entities):
#                 print(i, j, self.entities[i])
#                 resp = self.client.delete(
#                     f"/users/me/comparisons/{self.poll.name}/{self.entities[i].uid}/{self.entities[j].uid}/",
#                 )
#                 self.assertEqual(resp.status_code, 204, resp.content)
#             # call_command("ml_train")

#         # self.number_entities indiv score with 0.0 score
#         self.assertEqual(
#             ContributorRatingCriteriaScore.objects.filter(
#                 contributor_rating__user=self.user1
#             ).count(),
#             self.number_entities,
#         )
#         for (
#             contributorRatingCriteriaScore
#         ) in ContributorRatingCriteriaScore.objects.filter(
#             contributor_rating__user=self.user1
#         ).all():
#             self.assertEqual(contributorRatingCriteriaScore.score, 0.0)

#         # # no new global scores = self.number_entities
#         self.assertEqual(
#             EntityCriteriaScore.objects.filter(score_mode="default").count(),
#             self.number_entities,
#         )
