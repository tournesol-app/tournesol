from django.core.management.base import BaseCommand

from ml.inputs import MlInputFromDb
from ml.mehestan.run import run_mehestan
from tournesol.models import Poll
from tournesol.models.poll import ALGORITHM_LICCHAVI, ALGORITHM_MEHESTAN
from vouch.trust_algo import trust_algo


class Command(BaseCommand):
    """
    Runs Machine Learning task, to update scores periodically
    """
    help = "Runs the ml"

    def handle(self, *args, **options):
        # Update "trust_score" for all users
        trust_algo()

        # Update scores for all polls
        for poll in Poll.objects.filter(active=True):
            ml_input = MlInputFromDb(poll_name=poll.name)

            if poll.algorithm == ALGORITHM_MEHESTAN:
                run_mehestan(ml_input=ml_input, poll=poll)
            elif poll.algorithm == ALGORITHM_LICCHAVI:
                raise NotImplementedError("Licchavi is no longer supported")
            else:
                raise ValueError(f"unknown algorithm {repr(poll.algorithm)}'")
