""" Tournesol's AppConfig """

from django.apps import AppConfig


class TournesolConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tournesol"

    def ready(self):
        """Register the signal handlers at the start of the app, via import"""
        # pylint: disable=import-outside-toplevel,unused-import
        from . import signals  # noqa
