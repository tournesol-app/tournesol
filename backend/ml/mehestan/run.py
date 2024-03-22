import logging
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

from django import db
from django.conf import settings
from solidago.pipeline import TournesolInput
from solidago.pipeline.legacy2023.criterion_pipeline import run_pipeline_for_criterion
from solidago.pipeline.legacy2023.individual_scores import get_individual_scores

from core.models import User
from ml.inputs import MlInputFromDb
from ml.outputs import TournesolPollOutput, save_tournesol_scores
from tournesol.models import Poll

from .parameters import MehestanParameters

logger = logging.getLogger(__name__)


def update_user_scores(poll: Poll, user: User):
    params = MehestanParameters()
    ml_input = MlInputFromDb(poll_name=poll.name)
    for criteria in poll.criterias_list:
        output = TournesolPollOutput(poll_name=poll.name, criterion=criteria)
        scores = get_individual_scores(
            ml_input,
            criteria,
            parameters=params,
            single_user_id=user.pk,
        )
        scores["criteria"] = criteria
        scores.rename(
            columns={
                "score": "raw_score",
                "uncertainty": "raw_uncertainty",
            },
            inplace=True,
        )
        output.save_individual_scores(scores, single_user_id=user.pk)


def close_db_connection_callback():
    db.connection.close()


def run_mehestan(
    ml_input: TournesolInput, poll: Poll, parameters: MehestanParameters, main_criterion_only=False
):
    """
    This function use multiprocessing.

        1. Always close all database connections in the main process before
           creating forks. Django will automatically re-create new database
           connections when needed.

        2. Do not pass Django model's instances as arguments to the function
           run by child processes. Using such instances in child processes
           will raise an exception: connection already closed.

        3. Do not fork the main process within a code block managed by
           a single database transaction.

    See the indications to close the database connections:
        - https://www.psycopg.org/docs/usage.html#thread-and-process-safety
        - https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNECT

    See how django handles database connections:
        - https://docs.djangoproject.com/en/4.0/ref/databases/#connection-management
    """
    logger.info("Mehestan for poll '%s': Start", poll.name)

    criteria = poll.criterias_list

    criteria_to_run = [poll.main_criteria]
    if not main_criterion_only:
        criteria_to_run.extend(c for c in criteria if c != poll.main_criteria)

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
        futures = [
            executor.submit(
                run_pipeline_for_criterion,
                criterion=crit,
                input=ml_input,
                parameters=parameters,
                output=TournesolPollOutput(poll_name=poll.name, criterion=crit),
                # The callback fixes a warning about unclosed connections to test database
                done_callback=close_db_connection_callback,
            )
            for crit in criteria_to_run
        ]
        for fut in as_completed(futures):
            # reraise potential exception
            fut.result()

    save_tournesol_scores(poll)
    logger.info("Mehestan for poll '%s': Done", poll.name)
