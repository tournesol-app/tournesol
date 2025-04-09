import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import cache

from django import db
from django.conf import settings
from django.core.management.base import BaseCommand

import solidago

from ml.inputs import MlInputFromDb
from ml.outputs import TournesolPollOutput, save_tournesol_scores
from tournesol.models import EntityPollRating, Poll
from tournesol.models.poll import ALGORITHM_MEHESTAN, DEFAULT_POLL_NAME


@cache
def get_solidago_pipeline(run_trust_propagation: bool = True):
    return solidago.Sequential.load("ml/management/commands/tournesol_full.json")


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
            self.run_poll_pipeline(
                poll=poll,
                update_trust_scores=(not options["no_trust_algo"] and is_default_poll),
                main_criterion_only=options["main_criterion_only"],
            )

    def run_poll_pipeline(
        self,
        poll: Poll,
        update_trust_scores: bool,
        main_criterion_only: bool,
    ):
        pipeline = get_solidago_pipeline(
            run_trust_propagation=update_trust_scores
        )
        criteria_list = poll.criterias_list
        criteria_to_run = [poll.main_criteria]
        if not main_criterion_only:
            criteria_to_run.extend(
                c for c in criteria_list if c != poll.main_criteria
            )

        if settings.MEHESTAN_MULTIPROCESSING:
            # compute each criterion in parallel
            cpu_count = os.cpu_count() or 1
            cpu_count -= settings.MEHESTAN_KEEP_N_FREE_CPU
            os.register_at_fork(before=db.connections.close_all)
            executor = ProcessPoolExecutor(max_workers=max(1, cpu_count))
        else:
            # In tests, we might prefer to use a single thread to reduce overhead
            # of multiple processes, db connections, and redundant numba compilation
            executor = ThreadPoolExecutor(max_workers=1)

        with executor:
            futures = []
            for crit in criteria_to_run:
                pipeline_input = MlInputFromDb(poll_name=poll.name)
                pipeline_output = TournesolPollOutput(
                    poll_name=poll.name,
                    criterion=crit,
                    save_trust_scores_enabled=(update_trust_scores and crit == poll.main_criteria)
                )

                futures.append(
                    executor.submit(
                        self.run_pipeline_and_close_db,
                        pipeline=pipeline,
                        pipeline_input=pipeline_input,
                        pipeline_output=pipeline_output,
                        criterion=crit,
                    )
                )

            for fut in as_completed(futures):
                # reraise potential exception
                fut.result()

        save_tournesol_scores(poll)
        EntityPollRating.bulk_update_sum_trust_scores(poll)

        self.stdout.write(f"Pipeline for poll {poll.name}: Done")

    @staticmethod
    def run_pipeline_and_close_db(
        pipeline: Pipeline,
        pipeline_input: MlInputFromDb,
        pipeline_output: TournesolPollOutput,
        criterion: str
    ):
        pipeline.run(
            input=pipeline_input,
            criterion=criterion,
            output=pipeline_output,
        )
        # Closing the connection fixes a warning in tests
        # about open connections to the database.
        db.connection.close()
