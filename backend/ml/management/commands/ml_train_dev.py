"""
Machine Learning dev command file, see ml_train.py for production

USAGE:
- set env variable TOURNESOL_DEV to 1 to use this module
- run "python manage.py ml_train_dev"
"""

import logging
import gin

from django.core.management.base import BaseCommand

from ml.dev.experiments import run_experiment
from ml.core import TOURNESOL_DEV
from .ml_train import fetch_data


# parse parameters written in "hyperparameters_dev.gin"
gin.parse_config_file('ml/dev/hyperparameters_dev.gin')


class Command(BaseCommand):
    """ Django Command class """
    help = 'Runs the ml'

    def handle(self, *args, **options):
        comparison_data = fetch_data()
        if TOURNESOL_DEV:
            run_experiment(comparison_data)
        else:
            logging.error('You must turn TOURNESOL_DEV to 1 to run this')
