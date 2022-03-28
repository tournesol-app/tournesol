import logging

from django.core.management.base import BaseCommand

from backend.ml.inputs import MlInputFromDb
from ml.core import TOURNESOL_DEV
from ml.dev.experiments import run_experiment

"""
Machine Learning command file for developpement

Organisation:
- main developpement testing module, see ml_train for production
- Data is handled in "handle_data.py"
- ML model and decentralised structure are in "licchavi.py"
- Licchavi is called in "core.py"

USAGE:
- set env variable TOURNESOL_DEV to 1 to use this module
- run "python manage.py ml_train_dev"
"""


class Command(BaseCommand):
    help = 'Runs the ml'

    def handle(self, *args, **options):
        ml_input = MlInputFromDb(poll_name="videos")
        comparison_data_trusted = ml_input.get_comparisons(trusted_only=True)
        if TOURNESOL_DEV:
            run_experiment(comparison_data_trusted)
        else:
            logging.error('You must turn TOURNESOL_DEV to 1 to run this')
