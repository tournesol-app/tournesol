"""
Machine Learning command module

USAGE:
- run "python manage.py ml_train"
"""
import logging
import gin

from django.core.management.base import BaseCommand
from tournesol.models.video import (
    ComparisonCriteriaScore, ContributorRating,
    ContributorRatingCriteriaScore, VideoCriteriaScore)

from settings.settings import CRITERIAS
from ml.core import ml_run, TOURNESOL_DEV, HP_PATH


# parse parameters written in "hyperparameters.gin"
gin.parse_config_file(HP_PATH)


def fetch_data():
    """ Fetches the data from the Comparisons model

    Returns:
    - comparison_data: list of
        [   contributor_id: int, video_id_1: int, video_id_2: int,
            criteria: str, score: float, weight: float  ]
    """
    comparison_data = [
        [ccs.comparison.user_id, ccs.comparison.video_1_id,
            ccs.comparison.video_2_id, ccs.criteria, ccs.score, ccs.weight]
        for ccs
        in ComparisonCriteriaScore.objects.all().prefetch_related("comparison")
    ]
    return comparison_data


def save_data(video_scores, contributor_rating_scores):
    """
    Saves in the scores for Videos and ContributorRatings
    """
    VideoCriteriaScore.objects.all().delete()
    VideoCriteriaScore.objects.bulk_create([
        VideoCriteriaScore(
            video_id=video_id,
            criteria=criteria,
            score=score,
            uncertainty=uncertainty,
        )
        for video_id, criteria, score, uncertainty in video_scores
    ])

    rating_ids = {
        (contributor_id, video_id): rating_id
        for rating_id, contributor_id, video_id
        in ContributorRating.objects.all().values_list("id",
                                                       "user_id",
                                                       "video_id")
    }
    ratings_to_create = set(
        (contributor_id, video_id)
        for contributor_id, video_id, _, _, _
        in contributor_rating_scores
        if (contributor_id, video_id) not in rating_ids
    )
    created_ratings = ContributorRating.objects.bulk_create([
        ContributorRating(
            video_id=video_id,
            user_id=contributor_id,
            is_public=False,
        )
        for contributor_id, video_id in ratings_to_create
    ])
    rating_ids.update({
        (rating.user_id, rating.video_id): rating.id
        for rating in created_ratings
    })
    ContributorRatingCriteriaScore.objects.all().delete()
    ContributorRatingCriteriaScore.objects.bulk_create([
        ContributorRatingCriteriaScore(
            contributor_rating_id=rating_ids[(contributor_id, video_id)],
            criteria=criteria,
            score=score,
            uncertainty=uncertainty,
        )
        for contributor_id, video_id, criteria, score, uncertainty
        in contributor_rating_scores
    ])


class Command(BaseCommand):
    """ Django Command class """
    help = 'Runs the ml'

    def handle(self, *args, **options):
        comparison_data = fetch_data()
        if TOURNESOL_DEV:
            logging.error('You must turn TOURNESOL_DEV to 0 to use this')
        else:  # production mode
            glob_scores, loc_scores = ml_run(
                comparison_data,
                criterias=CRITERIAS,
                save=True,
                verb=-1
            )
            save_data(glob_scores, loc_scores)
