"""
Send an alert on Discord when the number of accounts using a trusted email
domain name exceeds a specific threshold on a given date.
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
    help = "Send an alert on Discord when the number of accounts using a" \
           " trusted email a trusted domain exceeds a defined threshold on a" \
           " given date."

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--date",
            type=validate_date,
            default=timezone.now().date(),
            help="Check the accounts created on that date (format yyyy-mm-dd).",
        )

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")
        self.stdout.write(f"date: {options['date']}")
        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")
