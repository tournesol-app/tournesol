from django.core.management.base import BaseCommand

from ml.inputs import MlInputFromDb
from ml.mehestan.run import run_mehestan
from tournesol.models import EntityPollRating, Poll
from tournesol.models.poll import ALGORITHM_LICCHAVI, ALGORITHM_MEHESTAN
from vouch.trust_algo import trust_algo


class Command(BaseCommand):
    help = "Runs Machine Learning tasks, to update scores periodically"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-trust-algo",
            action="store_true",
            help="Disable trust scores computation and preserve existing trust_score values",
        )

    def handle(self, *args, **options):
        if not options["no_trust_algo"]:
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
            self.stdout.write(f"Starting bulk update of sum_trust_score for poll {poll.name}")
            EntityPollRating.bulk_update_sum_trust_scores(poll)
            self.stdout.write(f"Finished bulk update of sum_trust_score for poll {poll.name}")
