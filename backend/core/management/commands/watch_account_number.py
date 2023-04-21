"""
Send an alert on Discord when the number of accounts using a trusted email
domain name exceeds a specific threshold on a given date.
"""
from argparse import ArgumentTypeError
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models.user import EmailDomain
from core.utils.email_domain import (
    get_domain_n_accounts_until,
    get_email_domain_with_recent_new_users,
)

THRESHOLDS = [3, 10, 50, 100, 200, 400, 600, 800, 1000, 1500, 2000]


def validate_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as err:
        raise ArgumentTypeError(err) from err


class Command(BaseCommand):
    help = (
        "Send an alert on Discord when the number of accounts using a"
        " trusted email a trusted domain exceeds a defined threshold on a"
        " given date."
    )

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

        day_before = options["date"] - timedelta(days=1)
        self.stdout.write(f"comparing {options['date']} with {day_before}")

        email_domains_since = get_email_domain_with_recent_new_users(
            options["date"], EmailDomain.STATUS_ACCEPTED, 1
        )

        for domain in email_domains_since:
            n_users_after = domain.cnt

            try:
                n_users_before = get_domain_n_accounts_until(domain.id, day_before)[0].cnt
            except IndexError:
                n_users_before = 0

            n_users_total = n_users_before + n_users_after

            try:
                threshold = max(
                    [thr for thr in THRESHOLDS if n_users_total >= thr > n_users_before]
                )
            except ValueError:
                continue

            msg = (
                f"{n_users_total} accounts use the trusted domain '{domain.domain}' - "
                f"the day before it was {n_users_before} (threshold exceeded: {threshold})"
            )
            self.stdout.write(msg)

        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")
