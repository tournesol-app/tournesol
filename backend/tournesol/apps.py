""" Tournesol's AppConfig """

from django.apps import AppConfig


class TournesolConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tournesol"

    def ready(self):
        from . import signals  # noqa: F401
        from tournesol.views.entities_to_compare import EntitiesToCompareView
        EntitiesToCompareView.get_ready()
