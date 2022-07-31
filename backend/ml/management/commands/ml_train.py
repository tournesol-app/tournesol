import logging

from django.core.management.base import BaseCommand

from core.models import User
from ml.core import TOURNESOL_DEV, ml_run
from ml.inputs import MlInputFromDb
from ml.mehestan.online_heuristics import run_online_heuristics
from ml.mehestan.run import run_mehestan
from ml.outputs import save_contributor_scores, save_entity_scores, save_tournesol_scores
from tournesol.models import Poll
from tournesol.models.poll import ALGORITHM_LICCHAVI, ALGORITHM_MEHESTAN

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
- ml_run() uses this data as input, trains via shape_train_predict()
     and returns video scores
- save_data() takes these scores and save them to the database
- these 3 are called by Django at the end of this file

USAGE:
- set env variable TOURNESOL_DEV to 1 for experimenting, don't for production
    mode
- run "python manage.py ml_train"
"""


def save_licchavi_data(
    entity_scores: list[tuple],
    contributor_rating_scores: list[tuple],
    poll: Poll,
    trusted_only=True,
):
    """
    Saves in the scores for Entities and ContributorRatings
    """
    trusted_user_ids = set(User.trusted_users().values_list("id", flat=True))

    if trusted_only:
        save_entity_scores(poll, entity_scores)
        save_tournesol_scores(poll)
        contributor_scores_to_save = [
            (contributor_id, video_id, criteria, score, uncertainty)
            for (
                contributor_id,
                video_id,
                criteria,
                score,
                uncertainty,
            ) in contributor_rating_scores
            if contributor_id in trusted_user_ids
        ]
    else:
        contributor_scores_to_save = [
            (contributor_id, video_id, criteria, score, uncertainty)
            for (
                contributor_id,
                video_id,
                criteria,
                score,
                uncertainty,
            ) in contributor_rating_scores
            if contributor_id not in trusted_user_ids
        ]

    save_contributor_scores(
        poll, contributor_scores_to_save, trusted_filter=trusted_only
    )


def process_licchavi(poll: Poll, ml_input: MlInputFromDb, trusted_only=True):
    poll_criterias_list = poll.criterias_list
    poll_comparison_df = ml_input.get_comparisons(trusted_only=trusted_only)

    # Transform DataFrame into list of lists
    poll_comparison_data = list(map(list, poll_comparison_df.itertuples(index=False)))

    glob_score, loc_score = ml_run(
        poll_comparison_data, criterias=poll_criterias_list, save=True, verb=-1
    )

    save_licchavi_data(glob_score, loc_score, poll, trusted_only=trusted_only)


class Command(BaseCommand):
    help = "Runs the ml"

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-untrusted",
            action="store_true",
            help="Skip ML run on untrusted users (for Licchavi only)",
        )
        parser.add_argument(
            "--online-heuristic",
            action="store_true",
            help="Run online heuristic for used_id, uid_a, uid_b",
        )
        parser.add_argument(
            "--unsave",
            action="store_true",
            help="run ml for indiv score but don't save",
        )
        parser.add_argument("--user_id")
        parser.add_argument("--uid_a")
        parser.add_argument("--uid_b")

    def handle(self, *args, **options):
        skip_untrusted = options["skip_untrusted"]
        online_heuristic = options["online_heuristic"]
        user_id = options["user_id"]
        unsave = options["unsave"]
        uid_a = options["uid_a"]
        uid_b = options["uid_b"]
        if TOURNESOL_DEV:
            logging.error("You must turn TOURNESOL_DEV to 0 to use this")
        else:  # production
            for poll in Poll.objects.filter(active=True):
                ml_input = MlInputFromDb(poll_name=poll.name)

                if poll.algorithm == ALGORITHM_LICCHAVI:
                    # Run for trusted users
                    logging.info(
                        "Licchavi for poll %s: Process on trusted users", poll.name
                    )
                    process_licchavi(poll, ml_input, trusted_only=True)

                    if not skip_untrusted:
                        # Run for all users including non trusted users
                        logging.info(
                            "Licchavi for poll %s: Process on all users", poll.name
                        )
                        process_licchavi(poll, ml_input, trusted_only=False)
                elif poll.algorithm == ALGORITHM_MEHESTAN:
                    if online_heuristic:
                        if user_id is None or uid_a is None or uid_b is None:
                            logging.warn(
                                "You should provide user_id, uid_a, uid_b with --online-heuristic"
                            )
                        else:
                            run_online_heuristics(
                                ml_input=ml_input,
                                poll=poll,
                                user_id=user_id,
                                uid_a=uid_a,
                                uid_b=uid_b,
                            )
                    else:
                        run_mehestan(ml_input=ml_input, poll=poll, unsave=unsave)
                else:
                    raise ValueError(f"unknown algorithm {repr(poll.algorithm)}'")
