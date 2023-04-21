"""
Send an alert on Discord when the number of account using a trusted domain
passes a threshold
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Send an alert on Discord when there are more users with" \
           "an email addresses considered trusted than a threshold X."

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")
        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")
