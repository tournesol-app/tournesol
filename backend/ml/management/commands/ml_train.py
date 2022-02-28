import logging

from django.core.management.base import BaseCommand

from core.models import User
from ml.core import TOURNESOL_DEV, ml_run
from tournesol.models import (
    ComparisonCriteriaScore,
    ContributorRating,
    ContributorRatingCriteriaScore,
    EntityCriteriaScore,
    Poll,
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


def fetch_data(trusted_only=True):
    """Fetches the data from the Comparisons model

    Returns:
    - comparison_data: list of
        [   contributor_id: int, video_id_1: int, video_id_2: int,
            criteria: str, score: float, weight: float  ]
    """
    comparisons_queryset = ComparisonCriteriaScore.objects.all().prefetch_related("comparison")
    
    if trusted_only:
        comparisons_queryset = comparisons_queryset.filter(comparison__user__in=User.trusted_users())
    comparison_data = [
            [
                ccs.comparison.user_id,
                ccs.comparison.entity_1_id,
                ccs.comparison.entity_2_id,
                ccs.criteria,
                ccs.score,
                ccs.weight,
            ]
            for ccs in comparisons_queryset
    ]

    return comparison_data


def save_data(video_scores, contributor_rating_scores, trusted_only=True):
    """
    Saves in the scores for Entities and ContributorRatings
    """
    default_poll_pk = Poll.default_poll_pk()
    trusted_user_ids = set(User.trusted_users().values_list("id", flat=True))

    if trusted_only:
        EntityCriteriaScore.objects.all().delete()
        EntityCriteriaScore.objects.bulk_create(
            [
                EntityCriteriaScore(
                    poll_id=default_poll_pk,
                    entity_id=video_id,
                    criteria=criteria,
                    score=score,
                    uncertainty=uncertainty,
                )
                for video_id, criteria, score, uncertainty in video_scores
            ]
        )

        contributor_scores_to_save = [
            (contributor_id, video_id, criteria, score, uncertainty)
            for (contributor_id, video_id, criteria, score, uncertainty) in contributor_rating_scores
            if contributor_id in trusted_user_ids
        ]
    else:
        contributor_scores_to_save = [
            (contributor_id, video_id, criteria, score, uncertainty)
            for (contributor_id, video_id, criteria, score, uncertainty) in contributor_rating_scores
            if contributor_id not in trusted_user_ids
        ]

    rating_ids = {
        (contributor_id, video_id): rating_id
        for rating_id, contributor_id, video_id in ContributorRating.objects.all().values_list(
            "id", "user_id", "entity_id"
        )
    }
    ratings_to_create = set(
        (contributor_id, video_id)
        for contributor_id, video_id, _, _, _ in contributor_scores_to_save
        if (contributor_id, video_id) not in rating_ids
    )
    created_ratings = ContributorRating.objects.bulk_create(
        ContributorRating(
            poll_id=default_poll_pk,
            entity_id=video_id,
            user_id=contributor_id,
        )
        for contributor_id, video_id in ratings_to_create
    )
    rating_ids.update(
        {(rating.user_id, rating.entity_id): rating.id for rating in created_ratings}
    )

    if trusted_only:
        ContributorRatingCriteriaScore.objects.filter(contributor_rating__user__in=User.trusted_users()).delete()
    else:
        ContributorRatingCriteriaScore.objects.exclude(contributor_rating__user__in=User.trusted_users()).delete()

    ContributorRatingCriteriaScore.objects.bulk_create(
        ContributorRatingCriteriaScore(
            contributor_rating_id=rating_ids[(contributor_id, video_id)],
            criteria=criteria,
            score=score,
            uncertainty=uncertainty,
        )
        for contributor_id, video_id, criteria, score, uncertainty in contributor_scores_to_save
    )

def process(trusted_only=True):
    criterias_list = Poll.default_poll().criterias_list
    comparison_data = fetch_data(trusted_only=trusted_only)
    glob_score, loc_score = ml_run(
        comparison_data, criterias=criterias_list, save=True, verb=-1
    )
    save_data(glob_score, loc_score, trusted_only=trusted_only)



class Command(BaseCommand):
    help = "Runs the ml"

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-untrusted',
            action="store_true",
            help='Skip ML run on untrusted users',
        )

    def handle(self, *args, **options):
        skip_untrusted = options['skip_untrusted']
        if TOURNESOL_DEV:
            logging.error('You must turn TOURNESOL_DEV to 0 to use this')
        else: #production
            # Run for trusted users
            logging.debug("Process on trusted users")
            process()

            if not skip_untrusted:
                # Run for all users including non trusted users
                logging.debug("Process on all users")
                process(trusted_only=False)
