""" Tournesol's AppConfig """

from django.apps import AppConfig


class TournesolConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tournesol"

    def ready(self):
        from tournesol.views.entities_to_compare import EntitiesToCompareView

        from . import signals  # noqa: F401

        EntitiesToCompareView.get_ready()
