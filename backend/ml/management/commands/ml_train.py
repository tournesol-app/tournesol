import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import cache

from django import db
from django.conf import settings
from django.core.management.base import BaseCommand

import solidago

from ml.state import TournesolState
from tournesol.models import EntityPollRating, Poll
from tournesol.models.poll import ALGORITHM_MEHESTAN, DEFAULT_POLL_NAME


class Command(BaseCommand):
    help = "Runs Machine Learning tasks, to update scores periodically"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-trust-algo",
            action="store_true",
            help="Disable trust scores computation and preserve existing trust_score values",
        )
        parser.add_argument("--main-criterion-only", action="store_true")

    def handle(self, *args, **options):
        for poll in Poll.objects.filter(active=True):
            if poll.algorithm != ALGORITHM_MEHESTAN:
                raise ValueError(f"Unknown algorithm {poll.algorithm!r}")

            is_default_poll = (poll.name == DEFAULT_POLL_NAME)
            self.run_poll(
                poll=poll,
                update_trust_scores=(not options["no_trust_algo"] and is_default_poll),
            )
    
    def run(self, poll_name, update_trust_scores):
        solidago.Sequential.load(
            "ml/management/commands/tournesol_full.json", 
            (os.cpu_count() or 1) - settings.MEHESTAN_KEEP_N_FREE_CPU,
            set() if update_trust_scores else {0}
        )(TournesolState.load(), poll.name)
        self.stdout.write(f"Pipeline for poll {poll.name}: Done")
