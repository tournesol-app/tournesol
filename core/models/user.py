import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator


from django_countries import countries

from ..utils.models import EnumList


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

