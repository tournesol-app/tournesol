"""
Send an alert on Discord when the number of account using a trusted domain
passes a threshold
"""
from argparse import ArgumentTypeError

from django.core.management.base import BaseCommand

from datetime import datetime
from django.utils import timezone


def validate_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError as err:
        raise ArgumentTypeError(err)


class Command(BaseCommand):
    help = "Send an alert on Discord if a threshold of users using" \
           "a trusted domain has been reached between the given date and the day before"

    def add_arguments(self, parser):

        parser.add_argument(
            "-d",
            "--date",
            type=validate_date,
            default=timezone.now().date(),
            help="count the accounts created on this date (format yyyy-mm-dd)",
        )

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")
        self.stdout.write(f"date: {options['date']}")
        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")
