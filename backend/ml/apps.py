""" apps.py """
from django.apps import AppConfig


class MlConfig(AppConfig):
    """ MLConfig Class """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml'
