"""
Delete users that have not activated their account.
"""
import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models.user import User
from settings import settings


class Command(BaseCommand):
    help = "Delete users that have not activated their account."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f"start command: {__name__}"))
        days_to_keep = settings.APP_CORE["MGMT_DELETE_INACTIVE_USERS_PERIOD"]

        # display the configuration if more verbosity is asked
        if options.get("verbosity", 1) > 1:
            self.stdout.write(
                self.style.SUCCESS(f"MGMT_DELETE_INACTIVE_USERS_PERIOD: {days_to_keep}")
            )

        delete_before = timezone.now() - datetime.timedelta(days=days_to_keep)
        n_users = User.objects.filter(
            is_active=False, date_joined__lt=delete_before
        ).count()
        self.stdout.write(self.style.SUCCESS(f"{n_users} inactive users found"))

        deleted = User.objects.filter(is_active=False).delete()
        self.stdout.write(self.style.SUCCESS(f"{deleted[0]} users deleted"))
        self.stdout.write(self.style.SUCCESS("end"))
