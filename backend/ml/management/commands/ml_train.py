import logging

from django.core.management.base import BaseCommand

from ml.inputs import MlInputFromDb
from ml.mehestan.online_heuristics import run_online_heuristics
from ml.mehestan.run import run_mehestan
from tournesol.models import Poll
from tournesol.models.poll import ALGORITHM_LICCHAVI, ALGORITHM_MEHESTAN


class Command(BaseCommand):
    """
    Runs Machine Learning task, to update scores periodically
    """
    help = "Runs the ml"

    def add_arguments(self, parser):
        parser.add_argument(
            "--online-heuristic",
            action="store_true",
            help="Run online heuristic for used_id, uid_a, uid_b",
        )
        parser.add_argument("--user_id")
        parser.add_argument("--uid_a")
        parser.add_argument("--uid_b")

    def handle(self, *args, **options):
        online_heuristic = options["online_heuristic"]
        user_id = options["user_id"]
        uid_a = options["uid_a"]
        uid_b = options["uid_b"]
        for poll in Poll.objects.filter(active=True):
            ml_input = MlInputFromDb(poll_name=poll.name)

            if poll.algorithm == ALGORITHM_LICCHAVI:
                raise NotImplementedError("Licchavi is no longer supported")
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
                    run_mehestan(ml_input=ml_input, poll=poll)
            else:
                raise ValueError(f"unknown algorithm {repr(poll.algorithm)}'")