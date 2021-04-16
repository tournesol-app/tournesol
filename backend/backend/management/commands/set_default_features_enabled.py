from django.core.management.base import BaseCommand
from backend.models import UserPreferences
from backend.constants import featureIsEnabledByDeFault
from backend.rating_fields import VIDEO_FIELDS


class Command(BaseCommand):
    """Set features enabled to default values for everyone."""
    def handle(self, **options):
        updated = UserPreferences.objects.update(**{
            f + "_enabled": featureIsEnabledByDeFault[f]
            for f in VIDEO_FIELDS
        })
        print("Updated", updated)
