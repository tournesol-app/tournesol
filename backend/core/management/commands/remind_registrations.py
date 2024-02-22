"""
Notify by email active users who haven't contributed after a defined period
following their registration.
"""

from datetime import timedelta
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, F, Q
from django.template.loader import render_to_string
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _

from core.models.user import User


class Command(BaseCommand):
    help = "Notify by email active users who haven't contributed after a"\
           " defined period following their registration."

    def get_subject(self):
        return "🌻 " + _("Would you like to help the research on responsible algorithms?")

    def get_message(self, n_comparisons):
        if n_comparisons > 0:
            return render_to_string("core/no_contrib_email/body_signup_contrib.txt")
        return render_to_string("core/no_contrib_email/body_no_contrib.txt")

    def get_html_message(self, n_comparisons):
        if n_comparisons > 0:
            return render_to_string("core/no_contrib_email/body_signup_contrib.html")
        return render_to_string("core/no_contrib_email/body_no_contrib.html")

    def notify_users(self, users):
        from_email = settings.REST_REGISTRATION["VERIFICATION_FROM_EMAIL"]

        fails = []
        successes = 0

        for user in users:
            if user.n_comp_after_signup > 0:
                continue

            try:
                lang_code = user.settings["general"]["notifications__lang"]
            except KeyError:
                lang_code = "en"

            translation.activate(lang_code)

            try:
                send_mail(
                    subject=self.get_subject(),
                    message=self.get_message(user.n_comp_signup),
                    html_message=self.get_html_message(user.n_comp_signup),
                    from_email=from_email,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except SMTPException as ex:
                fails.append((user.email, type(ex).__name__, ex))
            else:
                successes += 1

        return successes, fails

    def get_queryset(self, creation_date):
        period = timedelta(hours=16)

        return User.objects.filter(
            is_active=True,
            date_joined__date=creation_date.date(),
        ).annotate(
            n_comp_signup=Count(
                "comparisons",
                filter=Q(comparisons__datetime_add__lte=F("date_joined") + period),
            ),
            n_comp_after_signup=Count(
                "comparisons",
                filter=Q(comparisons__datetime_add__gt=F("date_joined") + period),
            ),
        )

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")

        no_contrib_period = settings.APP_CORE["MGMT_NO_CONTRIBUTION_REMINDER_PERIOD"]
        creation_date = timezone.now() - no_contrib_period

        if options.get("verbosity", 1) > 1:
            self.stdout.write(f"MGMT_NO_CONTRIBUTION_REMINDER_PERIOD: {no_contrib_period.days}")

        users = self.get_queryset(creation_date)
        successes, fails = self.notify_users(users)

        self.stdout.write(self.style.SUCCESS(f"users notified: {successes}"))

        if fails:
            self.stdout.write("some users have not been notified...")

            for fail in fails:
                self.stdout.write(f"email: {fail[0]} // {fail[1]}: {fail[2]}")

            raise CommandError(f"Failed to notify {len(fails)} users.")

        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")
