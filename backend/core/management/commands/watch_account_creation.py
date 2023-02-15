"""
Watch and alert when a certain number of accounts are created with the same trusted domaine.
"""
from django.core.management.base import BaseCommand

from core.lib.discord.api import write_in_channel
from core.utils.email_domain import get_user_cnt_per_email_domain
from core.utils.time import time_ago


class Command(BaseCommand):
    help = "Alert when a certain of accounts are created with the same trusted mail domain."

    def add_arguments(self, parser):

        parser.add_argument(
            "-s",
            "--since_n_hours",
            type=int,
            help="Number of hours ago to watch",
        )

        # Optional
        parser.add_argument(
            "-n",
            "--n_account",
            type=int,
            default=1,
            help="Number of account to raise alerting (default 1)",
        )

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")

        created_after = time_ago(hours=options["since_n_hours"])

        email_domains_alert_qs = get_user_cnt_per_email_domain(
            created_after, "ACK", options["n_account"]
        )

        for domain in email_domains_alert_qs:

            msg = (f"{domain.cnt} accounts created an account with '{domain.domain}' "
                   f"email domain in the last {options['since_n_hours']} hour(s)")
            self.stdout.write(msg)

            # Post the alert on Discord
            write_in_channel("infra_alert_private", msg)

        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")
