"""
Delete users that have not activated their account.
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from core.models.user import User
from settings import settings


class Command(BaseCommand):
    help = "Delete users that have not activated their account."

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")

        delta_to_keep = settings.APP_CORE["MGMT_DELETE_INACTIVE_USERS_PERIOD"]
        delete_before = timezone.now() - delta_to_keep

        # display the configuration if more verbosity is asked
        if options.get("verbosity", 1) > 1:
            self.stdout.write(
                f"MGMT_DELETE_INACTIVE_USERS_PERIOD: {delta_to_keep.days}"
            )

        # if at some point the `.delete()` method raises an exception, add the
        # corresponding try/catch and log the number of users to delete still
        # in the database
        deleted = User.objects.filter(
            Q(last_login__isnull=True) | Q(last_login__lt=delete_before),
            is_active=False,
            date_joined__lt=delete_before,
        ).delete()

        self.stdout.write(self.style.SUCCESS(f"{deleted[0]} users deleted"))
        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")
