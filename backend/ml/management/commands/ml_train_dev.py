import logging

from django.core.management.base import BaseCommand

from ml.core import TOURNESOL_DEV
from ml.dev.experiments import run_experiment

from .ml_train import fetch_data

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
        comparison_data = fetch_data()
        if TOURNESOL_DEV:
            run_experiment(comparison_data)
        else:
            logging.error('You must turn TOURNESOL_DEV to 1 to run this')
