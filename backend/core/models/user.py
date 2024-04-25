"""
User models and user preferences.
"""

import logging

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CheckConstraint, F, Func, Q, Value
from django.db.models.expressions import Exists, OuterRef
from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class User(AbstractUser):
    """
    Administrative, social and profile information about users.

    This model also contains application settings for each user,
    and methods related to email validation.
    """

    # Fields used by django-rest-registation to find a user.
    # Used by reset password mechanism.
    LOGIN_FIELDS = ("username", "email")

    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(
        max_length=100, blank=True, null=True, help_text="First name"
    )
    last_name = models.CharField(
        max_length=100, blank=True, null=True, help_text="Last name"
    )

    trust_score = models.FloatField(
        null=True,
        blank=True,
        default=None,
        help_text="The trust score assigned to the user based on trusted"
                  " domains and the vouching mechanism.",
    )

    settings = models.JSONField(
        null=False,
        blank=True,
        default=dict,
        help_text=_("The user' preferences.")
    )

    @classmethod
    def with_trusted_email(cls) -> QuerySet["User"]:
        accepted_domain = EmailDomain.objects.filter(
            domain=OuterRef("user_email_domain"), status=EmailDomain.STATUS_ACCEPTED
        )
        return (
            cls.objects.alias(
                # user_email_domain is extracted from user.email, with leading '@'
                user_email_domain=Lower(
                    Func(
                        F("email"),
                        Value(r"(.*)(@.*$)"),
                        Value(r"\2"),
                        function="regexp_replace",
                    )
                )
            )
            .alias(is_trusted=Exists(accepted_domain))
            .filter(is_trusted=True)
        )

    @classmethod
    def validate_email_unique_with_plus(cls, email: str, username="") -> str:
        """Raise ValidationError when similar emails are found in the database.

        Keyword arguments:
        email -- An email that is going to be written in the database.
        username -- The logged user's username, used to exclude him/herself from
                    the validation when updating its own email. Empty for
                    anonymous users.

        Emails considered similar when:
            - they share the same non-case-sensitive domain ;
            - they share, in the local part, the same non case-sensitive string
              before the `+` symbol.

        Examples of emails considered similar:
            - bob@example.org
            - bob+@example.org
            - bob+tournesol@example.org
            - BOB+tournesol@example.org
            - bob+hello@example.org
            - BOB+HELLO@example.org
            - etc.
        """
        email_split = email.rsplit("@", 1)

        # if there is no `@`, do nothing
        if len(email_split) == 1:
            return email

        local_part = email_split[0]
        local_part_split = local_part.split("+")

        users = User.objects.filter(
            Q(email__iexact=f"{local_part_split[0]}@{email_split[-1]}")
            | (
                Q(email__istartswith=f"{local_part_split[0]}+")
                & Q(email__iendswith=f"@{email_split[-1]}")
            ),
        )

        if username:
            users = users.exclude(username=username)

        if users.exists():
            # f-strings are incompatible with Django translations ("_")
            # pylint: disable=consider-using-f-string
            raise ValidationError(
                _(
                    "A user with an email starting with '%(email)s' already exists"
                    " in this domain." % {"email": f"{local_part_split[0]}+"}
                )
            )

        return email

    @property
    def has_trusted_email(self):
        return User.with_trusted_email().filter(pk=self.pk).exists()

    @property
    def is_trusted(self):
        # TODO: remove this property. Use 'has_trusted_email' instead,
        # and rename the associated field in the /accounts/profile/ API.
        return self.has_trusted_email

    def ensure_email_domain_exists(self):
        if not self.email:
            return
        if "@" not in self.email:
            # Should never happen, as the address format is validated by the field.
            logger.warning(
                'Cannot find email domain for user "%s" with email "%s".',
                self.username,
                self.email,
            )
            return
        _, domain_part = self.email.rsplit("@", 1)
        domain = f"@{domain_part}".lower()
        EmailDomain.objects.get_or_create(domain=domain)

    def get_recommendations_default_langs(self, poll: str):
        try:
            return self.settings[poll].get("recommendations__default_languages")
        except KeyError:
            return None

    def clean(self):
        value = self.email

        similar_email = User.objects.filter(email__iexact=value).exclude(pk=self.pk)

        if similar_email.exists():
            raise ValidationError(
                {"email": _("A user with this email address already exists.")}
            )

        try:
            User.validate_email_unique_with_plus(value, self.username)
        except ValidationError as error:
            # Catching the exception here allows us to add the email key, and
            # makes the message display near the email field in the admin
            # interface.
            raise ValidationError({"email": error.message}) from error

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        # No need to create the EmailDomain, if email is unchanged
        if update_fields is None or "email" in update_fields:
            self.ensure_email_domain_exists()
        return super().save(*args, **kwargs)

    def set_password(self, raw_password):
        super().set_password(raw_password)
        # Temporary workaround to force user activation
        # when a user asks for password reset
        self.is_active = True


class VerifiableEmail(models.Model):
    """One verified e-mail for a user."""

    email = models.EmailField(
        null=False, blank=False, help_text="E-mail address", max_length=100
    )
    is_verified = models.BooleanField(
        default=False, blank=False, null=False, help_text="Verified"
    )
    last_verification_email_ts = models.DateTimeField(
        help_text="Timestamp when the last verification e-mail was sent to this address",
        null=True,
        default=None,
        blank=True,
    )
    token = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="The token that needs to be supplied to verify this e-mail address",
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="User that this e-mail belongs to",
        null=True,
        related_name="verifiableemails",
    )
    rank = models.IntegerField(default=0, help_text="Ordering field")
    domain_fk = models.ForeignKey(
        to="EmailDomain",
        on_delete=models.SET_NULL,
        help_text="Foreign key to e-mail domain",
        null=True,
        related_name="verifiable_emails_domain",
        blank=True,
    )

    def save(self, *args, **kwargs):
        """Creating an e-mail domain entry if it does not exist."""
        domain = (
            f"@{str(self.email).split('@')[1]}" if str(self.email).split("@")[1] else ""
        )
        domain_object, _ = EmailDomain.objects.get_or_create(domain=domain)
        self.domain_fk = domain_object
        if self.pk is None:
            kwargs["force_insert"] = True
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ["rank"]
        unique_together = ["email", "user"]

    def __str__(self):
        return self.email


class EmailDomain(models.Model):
    """Domain which can be either accepted or rejected."""

    STATUS_REJECTED = "RJ"
    STATUS_ACCEPTED = "ACK"
    STATUS_PENDING = "PD"

    domain = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text="E-mail domain with leading @",
        unique=True,
    )
    status = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        default=STATUS_PENDING,
        help_text="Status of the domain.",
        choices=[
            (STATUS_REJECTED, "Rejected"),
            (STATUS_ACCEPTED, "Accepted"),
            (STATUS_PENDING, "Pending"),
        ],
    )
    datetime_add = models.DateTimeField(
        auto_now_add=True, help_text="Time the domain was added", null=True, blank=True
    )

    class Meta:
        ordering = ["-datetime_add", "domain"]
        constraints = [
            CheckConstraint(
                check=Q(domain__istartswith="@"),
                name="domain_starts_with_at",
            ),
        ]

    def __str__(self):
        """Get string representation."""
        return f"{self.domain} [{self.status}]"


class Degree(models.Model):
    """Educational degree."""

    level = models.CharField(
        null=False, blank=False, help_text="Degree level", max_length=100
    )
    domain = models.CharField(
        null=False, blank=False, help_text="Degree domain", max_length=100
    )
    institution = models.CharField(
        null=False, blank=False, help_text="Degree institution", max_length=100
    )
    user = models.ForeignKey(
        null=True,
        to=User,
        help_text="User that the degree belongs to.",
        on_delete=models.CASCADE,
        related_name="degrees",
    )
    rank = models.IntegerField(default=0, help_text="Ordering field")

    class Meta:
        ordering = ["rank", "level", "domain", "institution"]
        unique_together = ["level", "domain", "institution", "user"]

    def __str__(self):
        return f"{self.level}/{self.domain}/{self.institution}"


class Expertise(models.Model):
    """Expertise for a user."""

    name = models.CharField(
        null=False, blank=False, help_text="Expertise description", max_length=100
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="User for the expertise",
        related_name="expertises",
        null=True,
    )
    rank = models.IntegerField(default=0, help_text="Ordering field")

    class Meta:
        ordering = ["rank", "name"]
        unique_together = ["name", "user"]

    def __str__(self):
        return self.name


class ExpertiseKeyword(models.Model):
    """Expertise keyword for a user."""

    name = models.CharField(
        null=False,
        blank=False,
        help_text="Expertise keyword description",
        max_length=100,
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="User for the expertise keywords",
        related_name="expertise_keywords",
        null=True,
    )
    rank = models.IntegerField(default=0, help_text="Ordering field")

    class Meta:
        ordering = ["rank", "name"]
        unique_together = ["name", "user"]

    def __str__(self):
        return self.name
