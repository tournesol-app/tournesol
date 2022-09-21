"""
User models and user preferences.
"""

import logging

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, F, Func, Q, Value
from django.db.models.expressions import Exists, OuterRef
from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from django_countries import countries

from core.utils.models import WithDynamicFields, enum_list
from core.utils.validators import validate_avatar

logger = logging.getLogger(__name__)


class User(AbstractUser):
    """
    Administrative, social and profile information about users.
    (most of these fields are actually still unused)

    Contains methods for retrieving trusted and supertrusted users.
    """

    # Fields used by django-rest-registation to find a user.
    # Used by reset password mechanism.
    LOGIN_FIELDS = ("username", "email")

    email = models.EmailField(_("email address"), unique=True)
    is_demo = models.BooleanField(default=False, help_text="Is a demo account?")
    first_name = models.CharField(
        max_length=100, blank=True, null=True, help_text="First name"
    )
    last_name = models.CharField(
        max_length=100, blank=True, null=True, help_text="Last name"
    )
    title = models.TextField(null=True, blank=True, help_text="Your position")
    bio = models.TextField(
        null=True,
        blank=True,
        help_text="Self-description (other degrees, biography, ...)",
    )
    comment_anonymously = models.BooleanField(
        default=False, help_text="Comment anonymously by-default"
    )
    show_online_presence = models.BooleanField(
        default=False, help_text="Show my online presence on Tournesol"
    )
    show_my_profile = models.BooleanField(
        default=True, help_text="Show my profile on Tournesol"
    )
    birth_year = models.IntegerField(
        null=True,
        blank=True,
        help_text="Year of birth",
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
    )
    gender = models.CharField(
        max_length=50,
        help_text="Your gender",
        choices=enum_list("Not Specified", "Non-binary", "Other", "Female", "Male"),
        default="Not Specified",
    )
    nationality = models.CharField(
        max_length=100,
        help_text="Your country of nationality",
        choices=enum_list(*(["Not Specified"] + [x[1] for x in countries])),
        default="Not Specified",
    )

    residence = models.CharField(
        max_length=100,
        help_text="Your country of residence",
        choices=enum_list(*(["Not Specified"] + [x[1] for x in countries])),
        default="Not Specified",
    )

    race = models.CharField(
        max_length=50,
        help_text="Your ethnicity",
        choices=enum_list(
            "Not Specified",
            "African",
            "African American",
            "American Indian",
            "Arabic or Middle Eastern",
            "Asian",
            "Caucasian",
            "Latino or Hispanic",
            "Mixed",
            "Unknown",
            "Other",
        ),
        default="Not Specified",
    )
    political_affiliation = models.CharField(
        max_length=50,
        help_text="Your political preference",
        choices=enum_list(
            "Not Specified",
            "Extreme left",
            "Far left",
            "Left",
            "Centrist",
            "Right",
            "Far right",
            "Extreme right",
            "Other",
        ),
        default="Not Specified",
    )
    religion = models.CharField(
        max_length=50,
        help_text="Your religion",
        choices=enum_list(
            "Not Specified",
            "Christian",
            "Muslim",
            "Hindu",
            "Buddhist",
            "Jewish",
            "Atheist",
            "Agnostic",
            "Other",
        ),
        default="Not Specified",
    )
    degree_of_political_engagement = models.CharField(
        max_length=50,
        help_text="Your degree of political engagement",
        choices=enum_list(
            "Not Specified",
            "None",
            "Light",
            "Interested",
            "Engaged",
            "Activist",
            "Professional",
        ),
        default="Not Specified",
    )

    moral_philosophy = models.CharField(
        max_length=50,
        help_text="Your preferred moral philosophy",
        choices=enum_list(
            "Not Specified",
            "Utilitarian",
            "Non-Utilitarian Consequentialist",
            "Deontological",
            "Virtue Ethics",
            "Mixed",
            "Other",
        ),
        default="Not Specified",
    )

    website = models.URLField(
        help_text="Your website URL", blank=True, null=True, max_length=500
    )
    linkedin = models.URLField(
        help_text="Your LinkedIn URL", blank=True, null=True, max_length=500
    )
    youtube = models.URLField(
        help_text="Your Youtube channel URL", blank=True, null=True, max_length=500
    )
    google_scholar = models.URLField(
        help_text="Your Google Scholar URL",
        blank=True,
        null=True,
        default=None,
        max_length=500,
    )
    orcid = models.URLField(
        help_text="Your ORCID URL", blank=True, null=True, max_length=500
    )
    researchgate = models.URLField(
        help_text="Your Researchgate profile URL", blank=True, null=True, max_length=500
    )
    twitter = models.URLField(
        help_text="Your Twitter URL", blank=True, null=True, max_length=500
    )
    avatar = models.ImageField(
        upload_to="profiles",
        blank=True,
        help_text="Your profile picture.",
        validators=[validate_avatar],
        null=True,
    )
    voting_right = models.FloatField(
        null=True,
        blank=True,
        default=None,
        help_text="The voting right assigned to the user based on the vouching mechanism.",
    )

    # @property
    # def is_certified(self):
    #     """Check if the user's email is certified. See #152"""
    #     any_accepted = VerifiableEmail.objects.filter(
    #         user=self, is_verified=True, domain_fk__status=EmailDomain.STATUS_ACCEPTED
    #     )
    #     return True if any_accepted else False

    # @property
    # def is_domain_rejected(self):
    #     """Check if the user's email is certified. See #152"""
    #     any_rejected = VerifiableEmail.objects.filter(
    #         user=self, is_verified=True, domain_fk__status=EmailDomain.STATUS_REJECTED
    #     ).count()
    #     return True if any_rejected else False

    @classmethod
    def trusted_users(cls) -> QuerySet["User"]:
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
    def supertrusted_seed_users(cls) -> QuerySet["User"]:
        return cls.trusted_users().filter(is_staff=True)

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
    def is_trusted(self):
        return User.trusted_users().filter(pk=self.pk).exists()

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


# adding dynamic fields
WithDynamicFields.create_all()
