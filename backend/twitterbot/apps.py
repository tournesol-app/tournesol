"""
Defines AppConfig for Tournesol twitter bot app
"""

from django.apps import AppConfig


class TournesolConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "twitterbot"
