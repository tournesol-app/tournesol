"""
Defines AppConfig for Tournesol twitter bot app
"""

from django.apps import AppConfig


class TwitterBotConfig(AppConfig):
    """Twitter Bot AppConfig class"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "twitterbot"
