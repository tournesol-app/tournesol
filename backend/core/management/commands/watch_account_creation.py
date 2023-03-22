"""
Send an alert on Discord when too many users have created accounts using email
addresses considered trusted during the last hours.
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from core.lib.discord.api import write_in_channel
from core.models.user import EmailDomain
from core.utils.email_domain import get_email_domain_with_recent_new_users
from core.utils.time import time_ago


class Command(BaseCommand):
    help = "Send an alert on Discord when X users have created accounts using" \
           " email addresses considered trusted during the last Y hours."

    def add_arguments(self, parser):

        parser.add_argument(
            "-s",
            "--since-n-hours",
            type=int,
            help="Number of hours ago to watch",
        )

        # Optional
        parser.add_argument(
            "-n",
            "--n-accounts",
            type=int,
            default=1,
            help="Minimum number of created accounts required to raise an alert.",
        )

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")

        created_after = time_ago(hours=options["since_n_hours"])

        email_domains_alert_qs = get_email_domain_with_recent_new_users(
            created_after, EmailDomain.STATUS_ACCEPTED, options["n_accounts"]
        )

        for domain in email_domains_alert_qs:

            msg = (f"**{settings.MAIN_URL}** - {domain.cnt} accounts were created during the last "
                   f"{options['since_n_hours']} hour(s) with the domain '{domain.domain}'")

            self.stdout.write(msg)

            # Post the alert on Discord
            write_in_channel("infra_alert_private", msg)

        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")
