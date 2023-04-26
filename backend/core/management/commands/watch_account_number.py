"""
Send an alert on Discord when the number of accounts using a trusted email
domain name exceeds a specific threshold on a given date.
"""
from argparse import ArgumentTypeError
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.lib.discord.api import write_in_channel
from core.models.user import EmailDomain
from core.utils.email_domain import (
    count_accounts_by_domains_on_day,
    count_accounts_by_filtered_domains_until,
)

THRESHOLDS = [10, 50, 100, 200, 400, 600, 800, 1000, 1500, 2000]


def validate_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as err:
        raise ArgumentTypeError(err) from err


def send_on_discord(context: str, messages: list[str]):
    if messages:
        write_in_channel("infra_alert_private", context)

    for message in messages:
        write_in_channel("infra_alert_private", message)


class Command(BaseCommand):
    help = (
        "Send an alert on Discord when the number of accounts using an email "
        "with a trusted domain name exceeds a predefined threshold on a "
        "given date."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--date",
            type=validate_date,
            default=timezone.now().date(),
            help="Check the accounts created on that date (format yyyy-mm-dd).",
        )

        parser.add_argument(
            "-s",
            "--stdout-only",
            action='store_true',
            help="Display the results only in the standard output.",
        )

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")

        day_before = options["date"] - timedelta(days=1)

        # Get the number of accounts per domain created the `options["date"]`
        email_domains_since = count_accounts_by_domains_on_day(
            options["date"], EmailDomain.STATUS_ACCEPTED, 1
        )

        # Get the number of accounts per domain before `options["date"]`
        email_domains_before = count_accounts_by_filtered_domains_until(
            [domain.id for domain in email_domains_since], day_before, 1
        )

        context_msg = f"comparing {options['date']} with {day_before}"
        self.stdout.write(context_msg)

        alert_messages = []
        for domain in email_domains_since:
            try:
                n_users_before = next(
                    filter(lambda x, dom_id=domain.id: x.id == dom_id, email_domains_before)
                ).cnt
            except StopIteration:
                n_users_before = 0

            n_users_after = domain.cnt
            n_users_total = n_users_before + n_users_after

            try:
                threshold = max(
                    (thr for thr in THRESHOLDS if n_users_total >= thr > n_users_before)
                )
            except ValueError:
                continue

            msg = (
                f"**{settings.MAIN_URL}** - {n_users_total} accounts use the trusted domain"
                f" '{domain.domain}' - the day before it was {n_users_before} "
                f"(threshold exceeded: {threshold})"
            )
            self.stdout.write(msg)
            alert_messages.append(msg)

        # Post the alerts on Discord.
        if not options['stdout_only']:
            send_on_discord(context_msg, alert_messages)

        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")
