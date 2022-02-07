import logging

from django.core.management.base import BaseCommand

from ml.core import TOURNESOL_DEV, ml_run
from settings.settings import CRITERIAS
from tournesol.models import (
    ComparisonCriteriaScore,
    ContributorRating,
    ContributorRatingCriteriaScore,
    EntityCriteriaScore,
    User,
)

"""
Machine Learning main python file

Organisation:
- main file is here
- Data is handled in "handle_data.py"
- ML model and decentralised structure are in "licchavi.py"
- Licchavi is called in "core.py"

Notations:
- node = user : contributor
- vid = vID : video, video ID
- rating : rating provided by a contributor between 2 videos,
                                        in [0,100] or [-1,1]
- score : score of a video outputted by the algorithm, around [-2, 2]
- glob, loc : global, local
- idx, vidx : index, video index
- l_someting : list of someting
- arr : numpy array
- tens : torch tensor
- dic : dictionnary
- verb : verbosity level
- VARIABLE_NAME : global variable

Structure:
- fetch_data() provides data from the database
- ml_run() uses this data as input, trains via shape_train_predict()
     and returns video scores
- save_data() takes these scores and save them to the database
- these 3 are called by Django at the end of this file

USAGE:
- set env variable TOURNESOL_DEV to 1 for experimenting, don't for production
    mode
- run "python manage.py ml_train"
"""


def fetch_data():
    """Fetches the data from the Comparisons model

    Returns:
    - comparison_data: list of
        [   contributor_id: int, video_id_1: int, video_id_2: int,
            criteria: str, score: float, weight: float  ]
    """
    comparison_data = [
        [
            ccs.comparison.user_id,
            ccs.comparison.video_1_id,
            ccs.comparison.video_2_id,
            ccs.criteria,
            ccs.score,
            ccs.weight,
        ]
        for ccs in ComparisonCriteriaScore.objects
            .filter(comparison__user__in=User.trusted_users())
            .prefetch_related("comparison")
    ]
    return comparison_data


def save_data(video_scores, contributor_rating_scores):
    """
    Saves in the scores for Entities and ContributorRatings
    """
    EntityCriteriaScore.objects.all().delete()
    EntityCriteriaScore.objects.bulk_create(
        [
            EntityCriteriaScore(
                video_id=video_id,
                criteria=criteria,
                score=score,
                uncertainty=uncertainty,
            )
            for video_id, criteria, score, uncertainty in video_scores
        ]
    )

    rating_ids = {
        (contributor_id, video_id): rating_id
        for rating_id, contributor_id, video_id in ContributorRating.objects.all().values_list(
            "id", "user_id", "video_id"
        )
    }
    ratings_to_create = set(
        (contributor_id, video_id)
        for contributor_id, video_id, _, _, _ in contributor_rating_scores
        if (contributor_id, video_id) not in rating_ids
    )
    created_ratings = ContributorRating.objects.bulk_create(
        [
            ContributorRating(
                video_id=video_id,
                user_id=contributor_id,
            )
            for contributor_id, video_id in ratings_to_create
        ]
    )
    rating_ids.update(
        {(rating.user_id, rating.video_id): rating.id for rating in created_ratings}
    )
    ContributorRatingCriteriaScore.objects.all().delete()
    ContributorRatingCriteriaScore.objects.bulk_create(
        [
            ContributorRatingCriteriaScore(
                contributor_rating_id=rating_ids[(contributor_id, video_id)],
                criteria=criteria,
                score=score,
                uncertainty=uncertainty,
            )
            for contributor_id, video_id, criteria, score, uncertainty in contributor_rating_scores
        ]
    )


class Command(BaseCommand):
    help = "Runs the ml"

    def handle(self, *args, **options):
        comparison_data = fetch_data()
        if TOURNESOL_DEV:
            logging.error('You must turn TOURNESOL_DEV to 0 to use this')
        else:  # production mode
            glob_scores, loc_scores = ml_run(
                comparison_data, criterias=CRITERIAS, save=True, verb=-1
            )
            save_data(glob_scores, loc_scores)
