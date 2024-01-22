"""
Notify active users who haven't contributed since their account was created.
"""

from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q
from django.template.loader import render_to_string
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _

from core.models.user import User


class Command(BaseCommand):
    help = "Notify active users who haven't contributed since their account was created."

    def notify_users(self, users):
        from_email = settings.REST_REGISTRATION["VERIFICATION_FROM_EMAIL"]

        fails = []
        successes = 0

        subject_no_comp = _("Thank you for your registration")
        subject_signup_comp = _("Thank you for your contributions")

        for user in users:
            if user.n_comp_after_signup > 0:
                continue

            try:
                lang_code = user.settings["general"]["notifications__lang"]
            except KeyError:
                lang_code = "en"

            translation.activate(lang_code)

            msg_no_comp = render_to_string("core/no_contrib_email/body_no_contrib.txt")
            msg_signup_comp = render_to_string("core/no_contrib_email/body_signup_contrib.txt")
            html_msg_no_comp = render_to_string("core/no_contrib_email/body_no_contrib.html")
            html_msg_signup_comp = render_to_string(
                "core/no_contrib_email/body_signup_contrib.html"
            )

            if user.n_comp_signup > 0:
                subject = subject_signup_comp
                message = msg_signup_comp
                html_message = html_msg_signup_comp
            else:
                subject = subject_no_comp
                message = msg_no_comp
                html_message = html_msg_no_comp

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    html_message=html_message,
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
        return User.objects.filter(
            is_active=True,
            date_joined__date=creation_date.date(),
        ).annotate(
            n_comp_signup=Count(
                "comparisons",
                filter=Q(comparisons__datetime_add__date=creation_date.date()),
            ),
            n_comp_after_signup=Count(
                "comparisons",
                filter=Q(comparisons__datetime_add__date__gt=creation_date.date()),
            ),
        )

    def handle(self, *args, **options):
        self.stdout.write(f"start command: {__name__}")

        no_contrib_period = settings.APP_CORE["MGMT_NO_CONTRIBUTION_REMINDER_PERIOD"]
        creation_date = timezone.now() - no_contrib_period

        # display the configuration if more verbosity is asked
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
