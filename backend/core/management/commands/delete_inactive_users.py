"""
Delete users that have not activated their account.
"""
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.models.user import User

class Command(BaseCommand):
    help = 'Delete users that have not activated their account.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'start command: {__name__}'))

        delta = timezone.now() - datetime.timedelta(days=1)
        n_users = User.objects.filter(is_active=False, date_joined__lt=delta).count()
        self.stdout.write(self.style.SUCCESS(f'{n_users} inactive users found'))

        deleted = User.objects.filter(is_active=False).delete()
        self.stdout.write(self.style.SUCCESS(f'{deleted[0]} users deleted'))
        self.stdout.write(self.style.SUCCESS(f'{n_users - deleted[0]} were NOT deleted'))
        self.stdout.write(self.style.SUCCESS(f'end'))
