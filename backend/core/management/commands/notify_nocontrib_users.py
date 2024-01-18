"""
Notify active users who haven't contributed since their account was created.
"""
from datetime import datetime, timedelta
from smtplib import SMTPException

from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Count
from django.template.loader import render_to_string
from django.utils import timezone

from core.models.user import User
from tournesol.models import Comparison
from settings import settings


class Command(BaseCommand):
    help = "Notify active users who haven't contributed since their account was created."

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")

        from_email = settings.REST_REGISTRATION["VERIFICATION_FROM_EMAIL"]
        no_contrib_period = settings.APP_CORE["MGMT_NO_CONTRIBUTION_REMINDER_PERIOD"]

        creation_date = timezone.now() - no_contrib_period
        # creation_date = datetime(2022, 8, 22)

        # display the configuration if more verbosity is asked
        if options.get("verbosity", 1) > 1:
            self.stdout.write(f"MGMT_NO_CONTRIBUTION_REMINDER_PERIOD: {no_contrib_period.days}")

        users = (
            User.objects.filter(
                is_active=True,
                date_joined__date=creation_date.date(),
            )
            .annotate(
                n_comparisons=Count(
                    "comparisons",
                    filter=Q(comparisons__datetime_add__date__gt=creation_date.date()),
                )
            )
            .filter(n_comparisons=0)
        )

        html_message = render_to_string("core/no_contrib_email/body.html")

        fails = []
        successes = 0
        for user in users:
            try:
                send_mail(
                    subject="Subject here",
                    message="Here is the message.",
                    html_message=html_message,
                    from_email=from_email,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except SMTPException as ex:
                fails.append((user.email, type(ex).__name__, ex))
            else:
                successes += 1

        self.stdout.write(self.style.SUCCESS(f"users notified: {successes}"))

        if len(fails):
            self.stdout.write("some users have not been notified...")

            for fail in fails:
                self.stdout.write(f"email: {fail[0]} // {fail[1]}: {fail[2]}")

            raise CommandError(f"Failed to notify {len(fails)} users.")

        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")
