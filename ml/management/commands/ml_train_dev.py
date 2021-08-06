import logging
import gin

from django.core.management.base import BaseCommand

from ml.core import TOURNESOL_DEV
from .ml_train import fetch_data
from ml.dev.experiments import run_experiment


"""
Machine Learning main python file

Organisation:
- main developpement testing module, see ml_train for production
- Data is handled in "handle_data.py"
- ML model and decentralised structure are in "licchavi.py"
- Licchavi is called in "core.py"

USAGE:
- set env variable TOURNESOL_DEV to 1 to use this module
- run "python manage.py ml_train_dev"
"""

# parse parameters written in "hyperparameters_dev.gin"
gin.parse_config_file('ml/dev/hyperparameters_dev.gin')


class Command(BaseCommand):
    help = 'Runs the ml'

    def handle(self, *args, **options):
        comparison_data = fetch_data()
        if TOURNESOL_DEV:
            run_experiment(comparison_data)
        else:
            logging.error('You must turn TOURNESOL_DEV to 1 to run this')
