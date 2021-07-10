import uuid

from django.db import models
from django.db.models import Q, CheckConstraint
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from django_countries import countries

from ..utils.constants import featureIsEnabledByDeFault
from ..utils.models import EnumList, WithDynamicFields, WithFeatures
from ..utils.validators import validate_avatar
from settings.settings import MAX_VALUE, CRITERIAS, CRITERIAS_DICT


class User(AbstractUser):

    is_demo = models.BooleanField(default=False, help_text="Is a demo account?")
    first_name = models.CharField(max_length=100, blank=True, null=True, help_text="First name")
    last_name = models.CharField(max_length=100, blank=True, null=True, help_text="Last name")
    title = models.TextField(null=True, blank=True, help_text="Your position")
    bio = models.TextField(null=True, blank=True, help_text="Self-description (degree, biography, ...)")
    comment_anonymously = models.BooleanField(default=False, help_text="Comment anonymously by-default")
    show_online_presence = models.BooleanField(default=False, help_text="Show my online presence on Tournesol")
    show_my_profile = models.BooleanField(default=True, help_text="Show my profile on Tournesol")
    birth_year = models.IntegerField(null=True, blank=True, help_text="Year of birth",
                                     validators=[MinValueValidator(1900), MaxValueValidator(2100)])
    gender = models.CharField(
        max_length=50,
        help_text="Your gender",
        choices=EnumList(
            'Not Specified',
            'Non-binary',
            'Other',
            'Female',
            'Male'),
        default='Not Specified')
    nationality = models.CharField(
        max_length=100,
        help_text="Your country of nationality",
        choices=EnumList(*(["Not Specified"] + [x[1] for x in countries])),
        default="Not Specified")

    residence = models.CharField(
        max_length=100,
        help_text="Your country of residence",
        choices=EnumList(*(["Not Specified"] + [x[1] for x in countries])),
        default="Not Specified")

    race = models.CharField(
        max_length=50,
        help_text="Your ethnicity",
        choices=EnumList(
            'Not Specified',
            'African',
            'African American',
            'American Indian',
            'Arabic or Middle Eastern',
            'Asian',
            'Caucasian',
            'Latino or Hispanic',
            'Mixed',
            'Unknown',
            'Other'),
        default='Not Specified')
    political_affiliation = models.CharField(
        max_length=50,
        help_text="Your political preference",
        choices=EnumList(
            'Not Specified',
            'Extreme left',
            'Far left',
            'Left',
            'Centrist',
            'Right',
            'Far right',
            'Extreme right',
            'Other'
        ),
        default='Not Specified')
    religion = models.CharField(
        max_length=50,
        help_text="Your religion",
        choices=EnumList(
            'Not Specified',
            'Christian',
            'Muslim',
            'Hindu',
            'Buddhist',
            'Jewish',
            'Atheist',
            'Agnostic',
            'Other'
        ),
        default='Not Specified')
    degree_of_political_engagement = models.CharField(
        max_length=50,
        help_text="Your degree of political engagement",
        choices=EnumList(
            'Not Specified',
            'None',
            'Light',
            'Interested',
            'Engaged',
            'Activist',
            'Professional'
        ),
        default='Not Specified')

    moral_philosophy = models.CharField(
        max_length=50,
        help_text="Your preferred moral philosophy",
        choices=EnumList(
            'Not Specified',
            'Utilitarian',
            'Non-Utilitarian Consequentialist',
            'Deontological',
            'Virtue Ethics',
            'Mixed',
            'Other'
        ),
        default='Not Specified'
    )

    website = models.URLField(
        help_text="Your website URL",
        blank=True,
        null=True,
        max_length=500)
    linkedin = models.URLField(
        help_text="Your LinkedIn URL",
        blank=True,
        null=True,
        max_length=500)
    youtube = models.URLField(
        help_text="Your Youtube channel URL",
        blank=True,
        null=True,
        max_length=500)
    google_scholar = models.URLField(
        help_text="Your Google Scholar URL",
        blank=True,
        null=True,
        default=None,
        max_length=500)
    orcid = models.URLField(
        help_text="Your ORCID URL",
        blank=True,
        null=True,
        max_length=500)
    researchgate = models.URLField(
        help_text="Your Researchgate profile URL",
        blank=True,
        null=True,
        max_length=500)
    twitter = models.URLField(
        help_text="Your Twitter URL",
        blank=True,
        null=True,
        max_length=500)
    avatar = models.ImageField(
        upload_to="profiles",
        blank=True,
        help_text="Your profile picture.",
        validators=[validate_avatar],
        null=True)

    @property
    def user_preferences(self):
        """Preferences for this user."""
        return UserPreferences.objects.get(user=self)

    @property
    def is_certified(self):
        """Check if the user's email is certified. See #152"""
        any_accepted = VerifiableEmail.objects.filter(
            user=self,
            is_verified=True,
            domain_fk__status=EmailDomain.STATUS_ACCEPTED)
        return True if any_accepted else False

    @property
    def is_domain_rejected(self):
        """Check if the user's email is certified. See #152"""
        any_rejected = VerifiableEmail.objects.filter(
            user=self,
            is_verified=True,
            domain_fk__status=EmailDomain.STATUS_REJECTED).count()
        return True if any_rejected else False


class UserPreferences(models.Model, WithFeatures, WithDynamicFields):
    """One user with preferences."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        help_text="User that preferences belong to", related_name='userpreferences')

    rating_mode = models.CharField(max_length=50, default='enable_all',
                                   help_text="Which sliders and parameters to display"
                                             " on the rating page?",
                                   choices=EnumList('enable_all', 'skip', 'confidence'))

    @staticmethod
    def _create_fields():
        """Adding score fields."""
        for field in CRITERIAS:
            UserPreferences.add_to_class(
                field,
                models.FloatField(
                    default=0.0,
                    blank=False,
                    help_text=CRITERIAS_DICT[field],
                    validators=[
                        MinValueValidator(0.0),
                        MaxValueValidator(MAX_VALUE)]))

            UserPreferences.add_to_class(
                field + '_enabled',
                models.BooleanField(
                    default=featureIsEnabledByDeFault[field],
                    blank=False,
                    help_text=f"{field} given for ratings"))

    # center ratings around MAX_RATING / 2
    VECTOR_OFFSET = MAX_VALUE / 2

    def __str__(self):
        return str(self.user)

    @property
    def username(self):
        """DjangoUser username."""
        return self.user.username


class VerifiableEmail(models.Model):
    """One verified e-mail for a user."""
    email = models.EmailField(
        null=False,
        blank=False,
        help_text="E-mail address",
        max_length=100)
    is_verified = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="Verified")
    last_verification_email_ts = models.DateTimeField(
        help_text="Timestamp when the last verification e-mail was sent to this address",
        null=True,
        default=None,
        blank=True)
    token = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="The token that needs to be supplied to verify this e-mail address")
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="User that this e-mail belongs to",
        null=True,
        related_name='verifiableemails')
    rank = models.IntegerField(default=0, help_text="Ordering field")
    domain_fk = models.ForeignKey(
        to='EmailDomain',
        on_delete=models.SET_NULL,
        help_text="Foreign key to e-mail domain",
        null=True,
        related_name='verifiable_emails_domain',
        blank=True)

    def save(self, *args, **kwargs):
        """Creating an e-mail domain entry if it does not exist."""
        domain = f"@{str(self.email).split('@')[1]}" if str(self.email).split('@')[1] else ""
        domain_object, _ = EmailDomain.objects.get_or_create(domain=domain)
        self.domain_fk = domain_object
        if self.pk is None:
            kwargs['force_insert'] = True
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['rank']
        unique_together = ['email', 'user']

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
        unique=True)
    status = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        default=STATUS_PENDING,
        help_text="Status of the domain.",
        choices=[
            (STATUS_REJECTED,
             "Rejected"),
            (STATUS_ACCEPTED,
             "Accepted"),
            (STATUS_PENDING,
             "Pending"),
        ])
    datetime_add = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the domain was added",
        null=True,
        blank=True)

    class Meta:
        ordering = ['-datetime_add', 'domain']
        constraints = [
            CheckConstraint(
                check=Q(domain__istartswith='@'),
                name='domain_starts_with_at',
            ),
        ]

    def __str__(self):
        """Get string representation."""
        return f"{self.domain} [{self.status}]"


class Degree(models.Model):
    """Educational degree."""
    level = models.CharField(
        null=False,
        blank=False,
        help_text="Degree level",
        max_length=100)
    domain = models.CharField(
        null=False,
        blank=False,
        help_text="Degree domain",
        max_length=100)
    institution = models.CharField(
        null=False,
        blank=False,
        help_text="Degree institution",
        max_length=100)
    user = models.ForeignKey(
        null=True,
        to=User,
        help_text="User that the degree belongs to.",
        on_delete=models.CASCADE,
        related_name='degrees')
    rank = models.IntegerField(default=0, help_text="Ordering field")

    class Meta:
        ordering = ['rank', 'level', 'domain', 'institution']
        unique_together = ['level', 'domain', 'institution', 'user']

    def __str__(self):
        return f"{self.level}/{self.domain}/{self.institution}"


class Expertise(models.Model):
    """Expertise for a user."""
    name = models.CharField(
        null=False,
        blank=False,
        help_text="Expertise description",
        max_length=100)
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="User for the expertise",
        related_name="expertises",
        null=True)
    rank = models.IntegerField(default=0, help_text="Ordering field")

    class Meta:
        ordering = ['rank', 'name']
        unique_together = ['name', 'user']

    def __str__(self):
        return self.name


class ExpertiseKeyword(models.Model):
    """Expertise keyword for a user."""
    name = models.CharField(
        null=False,
        blank=False,
        help_text="Expertise keyword description",
        max_length=100)
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="User for the expertise keywords",
        related_name="expertise_keywords",
        null=True)
    rank = models.IntegerField(default=0, help_text="Ordering field")

    class Meta:
        ordering = ['rank', 'name']
        unique_together = ['name', 'user']

    def __str__(self):
        return self.name

# adding dynamic fields
WithDynamicFields.create_all()
