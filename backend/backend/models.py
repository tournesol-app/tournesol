"""Note that some fields are added dynamically below!"""

import datetime
import hashlib
import logging
import os
import uuid
from functools import reduce

import computed_property
import numpy as np
from backend.black_white_email_domain import get_domain
from backend.model_helpers import WithFeatures, WithEmbedding, WithDynamicFields, EnumList,\
    url_has_domain
from backend.rating_fields import MAX_VALUE as MAX_RATING
from backend.rating_fields import VIDEO_FIELDS, VIDEO_FIELDS_DICT, MAX_FEATURE_WEIGHT
from backend.video_search import VideoSearchEngine
from django.contrib.auth.models import User as DjangoUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CheckConstraint
from django.db.models import Q, F, Count, Func, Sum, Value, FloatField, IntegerField, Case, When,\
    BooleanField
from django.utils.timezone import make_aware
from django_countries import countries
from languages.fields import LanguageField
from backend.constants import featureIsEnabledByDeFault, youtubeVideoIdRegex
from django.core.validators import RegexValidator
from simple_history import register as register_historical


class ResetPasswordToken(models.Model):
    """Token to reset passwords."""
    user = models.ForeignKey(to=DjangoUser,
                             on_delete=models.CASCADE,
                             help_text="User that this reset"
                                       " password sessino belongs to",
                             null=False)
    token = models.CharField(max_length=1000, blank=False, null=False,
                             help_text="A token that the user must show"
                                       " to log in and be able to reset the password")

    class Meta:
        unique_together = ['user', 'token']

    def __str__(self):
        return str(self.user)


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
        to='UserInformation',
        on_delete=models.CASCADE,
        help_text="User that this e-mail belongs to",
        null=True,
        related_name='emails')
    rank = models.IntegerField(default=0, help_text="Ordering field")
    domain = computed_property.ComputedCharField(
        compute_from='email_domain',
        max_length=50,
        default=uuid.uuid1,
        help_text="Email domain with @")
    domain_fk = models.ForeignKey(
        to='EmailDomain',
        on_delete=models.SET_NULL,
        help_text="Foreign key to e-mail domain",
        null=True,
        related_name='verifiable_emails_domain',
        blank=True)

    def email_domain(self):
        """Get e-mail domain."""
        return get_domain(self.email)

    def save(self, *args, **kwargs):
        """Creating an e-mail domain entry if it does not exist."""
        domain = self.email_domain()
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


class Expertise(models.Model):
    """Expertise for a user."""
    name = models.CharField(
        null=False,
        blank=False,
        help_text="Expertise description",
        max_length=100)
    user = models.ForeignKey(
        to='UserInformation',
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
        to='UserInformation',
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
        to='UserInformation',
        help_text="User that the degree belongs to.",
        on_delete=models.CASCADE,
        related_name='degrees')
    rank = models.IntegerField(default=0, help_text="Ordering field")

    class Meta:
        ordering = ['rank', 'level', 'domain', 'institution']
        unique_together = ['level', 'domain', 'institution', 'user']

    def __str__(self):
        return f"{self.level}/{self.domain}/{self.institution}"


class UserInformation(models.Model):
    """All information about a Tournesol user."""
    user = models.OneToOneField(
        DjangoUser,
        on_delete=models.CASCADE,
        help_text="DjangoUser that the info belong to")
    first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="First name")
    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Last name")
    title = models.TextField(null=True, blank=True, help_text="Your position")
    bio = models.TextField(
        null=True,
        blank=True,
        help_text="Self-description (degree, biography, ...)")
    comment_anonymously = models.BooleanField(
        default=False, help_text="Comment anonymously by-default")
    show_online_presence = models.BooleanField(
        default=False, help_text="Show my online presence on Tournesol")
    show_my_profile = models.BooleanField(
        default=True, help_text="Show my profile on Tournesol")
    birth_year = models.IntegerField(
        null=True,
        blank=True,
        help_text="Year of birth",
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2100)])
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

    # URL constraints, see #324
    # enforced in save()
    _domain_startswith = {
        'twitter': 'twitter.com',
        'linkedin': 'www.linkedin.com',
        'youtube': 'www.youtube.com',
        'google_scholar': 'scholar.google.com',
        'orcid': 'orcid.org',
        'researchgate': 'www.researchgate.net',
    }

    avatar_hash = computed_property.ComputedCharField(
        compute_from='get_avatar_hash',
        max_length=50,
        default=uuid.uuid1,
        help_text="Hash for the image.")

    is_demo = models.BooleanField(default=False, help_text="Is a demo account?")

    def get_avatar_hash(self):
        """Compute hash function for the image."""
        if self.avatar:
            # for uploaded files
            if hasattr(self.avatar, 'path') and os.path.isfile(self.avatar.path):
                with open(self.avatar.path, 'rb') as f:
                    data = f.read()
            else:  # for uploads
                data = self.avatar.read()
            self.avatar.seek(0)
            result = hashlib.md5(data).hexdigest()
        else:
            result = ""
        return result

    def save(self, *args, **kwargs):
        """Custom save, checks if there already is an image."""
        if self.avatar:
            # validating image size
            # try:?
            UserInformation.validate_avatar(self.avatar)

            # re-using old image
            myhash = self.avatar_hash
            fltr = UserInformation.objects.filter(avatar_hash=myhash)
            if fltr.count():
                # re-writing the field if hash is the same
                self.avatar = fltr.first().avatar
                logging.info(f"Re-using avatar {self.avatar}")

        # recomputing the property
        _ = self.avatar_hash

        # print("Uploaded file hash", self.avatar_hash)

        for service, domain in self._domain_startswith.items():
            if not url_has_domain(getattr(self, service, None),
                                  domain):
                raise ValidationError({service: f"This URL must have {domain} as its domain."})

        return super(UserInformation, self).save(*args, **kwargs)

    def validate_avatar(fieldfile_obj, mb_limit=5):
        """Check avatar size.

        https://stackoverflow.com/questions/6195478/max-image-size-on-file-upload.
        """
        # print("VALIDATION", fieldfile_obj, fieldfile_obj.size)
        filesize = fieldfile_obj.size
        if filesize > mb_limit * 1024 * 1024:
            raise ValidationError(
                {"avatar": "Max file size is %s MB" % str(mb_limit)})

    avatar = models.ImageField(
        upload_to="profiles",
        blank=True,
        help_text="Your profile picture.",
        validators=[validate_avatar],
        null=True)

    def __str__(self):
        return str(self.user)

    @property
    def username(self):
        """DjangoUser username."""
        return self.user.username

    @property
    def user_preferences(self):
        """Preferences for this user."""
        return UserPreferences.objects.get(user=self.user)

    @property
    def n_ratings(self):
        """Number of ratings given by this user."""
        return ExpertRating.objects.filter(user=self.user_preferences).count()

    @property
    def n_videos(self):
        """Number of videos rated by this user."""
        return Video.objects.filter(Q(expertrating_video_1__user=self.user_preferences) | Q(
            expertrating_video_2__user=self.user_preferences)).values('video_id').distinct().count()

    @property
    def n_comments(self):
        """Number of comments by a given user."""
        return VideoComment.objects.filter(user=self.user_preferences).count()

    @property
    def n_thanks_given(self):
        """Number of thanks yous for recommendations given."""
        return VideoRatingThankYou.objects.filter(thanks_from=self.user_preferences).count()

    @property
    def n_thanks_received(self):
        """Number of thanks yous for recommendations received."""
        return VideoRatingThankYou.objects.filter(thanks_to=self.user_preferences).count()

    @property
    def n_public_videos(self):
        """Number of videos rated publicly."""
        qs = VideoRating.objects.filter(user=self.user_preferences)
        qs = VideoRatingPrivacy._annotate_privacy(qs=qs, prefix='video__videoratingprivacy',
                                                  field_user=F('user'))
        qs = qs.filter(_is_public=True)
        return qs.count()

    @property
    def n_likes(self):
        """Total number of likes - dislikes for all comments by this user."""
        queryset = VideoComment.objects.filter(user=self.user_preferences)
        queryset = queryset.annotate(
            votes_plus_=Count(
                'videocommentmarker_comment', filter=Q(
                    videocommentmarker_comment__which="vote_plus")), votes_minus_=Count(
                'videocommentmarker_comment', filter=Q(
                    videocommentmarker_comment__which="vote_minus")))
        queryset = queryset.annotate(
            like_cnt=F('votes_plus_') - F('votes_minus_'))
        result = queryset.aggregate(like_sum=Sum('like_cnt'))['like_sum']
        if result is None:
            return 0
        return result

    @property
    def n_mentions(self, trigger='@', separator=''):
        """Number of times a user is mentioned in the comments."""
        search_str = f"{trigger}{self.user.username}"
        return VideoComment.objects.filter(comment__icontains=search_str).count()

    @property
    def is_certified(self):
        """Check if the user's email is certified. See #152"""
        any_accepted = VerifiableEmail.objects.filter(
            user=self,
            is_verified=True,
            domain_fk__status=EmailDomain.STATUS_ACCEPTED).count()
        return any_accepted > 0

    @property
    def is_domain_rejected(self):
        """Check if the user's email is certified. See #152"""
        any_rejected = VerifiableEmail.objects.filter(
            user=self,
            is_verified=True,
            domain_fk__status=EmailDomain.STATUS_REJECTED).count()
        return any_rejected > 0

    @staticmethod
    def _annotate_is_certified(queryset, prefix=""):
        """Annotate a queryset with _is_certified in a vectorized way."""
        queryset = queryset.annotate(
            _certified_emails=Count(
                prefix + 'emails',
                filter=Q(**{
                    prefix + 'emails__domain_fk__status': EmailDomain.STATUS_ACCEPTED,
                    prefix + 'emails__is_verified': True
                })))
        queryset = queryset.annotate(_is_certified=Case(When(
            Q(_certified_emails__gt=0), then=1), default=0, output_field=IntegerField()))
        return queryset

    @staticmethod
    def _annotate_n_public_videos(qs, prefix=""):
        """Get _n_public_videos field."""

        qs = VideoRatingPrivacy._annotate_privacy(
            qs=qs, prefix='user__userpreferences__videoratingprivacy',
            annotate_n=True, annotate_bool=False,
            field_user=F('user__userpreferences'),
            videorating_field='user__userpreferences__videorating'
        )

        qs = qs.annotate(_n_public_videos=F('_n_public'))
        return qs


class Video(models.Model, WithFeatures, WithEmbedding, WithDynamicFields):
    """One video."""
    video_id_regex = RegexValidator(youtubeVideoIdRegex,
                                    f'Video ID must match {youtubeVideoIdRegex}')

    video_id = models.CharField(
        max_length=20,
        unique=True,
        help_text=f"Video ID from YouTube URL, matches {youtubeVideoIdRegex}",
        validators=[video_id_regex])
    name = models.CharField(max_length=1000, help_text="Video Title",
                            blank=True)
    description = models.TextField(
        null=True, help_text="Video Description from the web page",
        blank=True)
    caption_text = models.TextField(
        null=True, help_text="Processed video caption (subtitle) text",
        blank=True)
    embedding = models.BinaryField(
        null=True,
        help_text="NumPy array with BERT embedding for caption_text, shape("
                  "EMBEDDING_LEN,)")
    info = models.TextField(
        null=True, blank=True,
        help_text="Additional information (json)")
    duration = models.DurationField(null=True, help_text="Video duration", blank=True)
    language = LanguageField(
        null=True, blank=True,
        max_length=10,
        help_text="Language of the video")
    publication_date = models.DateField(
        null=True, help_text="Video publication date", blank=True)
    metadata_timestamp = models.DateTimeField(blank=True,
                                              null=True,
                                              help_text="Timestamp the metadata was uploaded")
    views = models.IntegerField(null=True, help_text="Number of views", blank=True)
    uploader = models.CharField(
        max_length=1000,
        null=True, blank=True,
        help_text="Name of the channel (uploader)")

    add_time = models.DateTimeField(null=True,
                                    auto_now_add=True,
                                    help_text="Time the video was added to Tournesol")
    last_download_time = models.DateTimeField(null=True,
                                              blank=True,
                                              help_text="Last time download of metadata"
                                                        " was attempted")
    wrong_url = models.BooleanField(default=False,
                                    help_text="Is the URL incorrect")
    is_unlisted = models.BooleanField(default=False, help_text="Is the video unlisted")
    download_attempts = models.IntegerField(default=0, help_text="Number of times video"
                                                                 " was downloaded")
    download_failed = models.BooleanField(
        default=False, help_text="Was last download unsuccessful")

    @staticmethod
    def get_or_create_with_validation(**kwargs):
        """Get an object or validate data and create."""
        qs = Video.objects.filter(**kwargs)
        if qs.count() == 1:
            return qs.get()
        elif qs.count() > 1:
            raise ValueError("Queryset contains more than one item")
        else:
            video = Video(**kwargs)
            video.full_clean()
            video.save()
            return video

    @staticmethod
    def _create_fields():
        """Adding score fields."""
        for field in VIDEO_FIELDS:
            # adding the field to user preferences
            Video.add_to_class(
                field,
                models.FloatField(
                    default=0,
                    blank=False,
                    help_text=VIDEO_FIELDS_DICT[field]))

        for field in VIDEO_FIELDS:
            # adding the field to user preferences
            Video.add_to_class(
                field + "_uncertainty",
                models.FloatField(
                    default=0,
                    blank=False,
                    help_text=f"Uncertainty for {field}"))

    @property
    def best_text(self, min_len=5):
        """Return caption of present, otherwise description, otherwise title."""
        priorities = [self.caption_text, self.description, self.name]

        # going over all priorities
        for v in priorities:
            # selecting one that exists
            if v is not None and len(v) >= min_len:
                return v
        return None

    @property
    def pareto_optimal(self):
        def query_or(lst):
            return reduce((lambda x, y: x | y), lst)

        def query_and(lst):
            return reduce((lambda x, y: x & y), lst)

        f1 = query_and([Q(**{f + "__gte": getattr(self, f)}) for f in VIDEO_FIELDS])
        f2 = query_or([Q(**{f + "__gt": getattr(self, f)}) for f in VIDEO_FIELDS])

        qs = Video.objects.filter(f1).filter(f2)
        return qs.count() == 0

    @property
    def all_text(self):
        """Return concat of caption, description, title."""
        options = [self.caption_text, self.description, self.name]
        options = filter(lambda x: x is not None, options)
        return ' '.join(options)

    @property
    def short_text(self):
        options = [self.name, self.uploader, self.description]
        options = filter(lambda x: x is not None, options)
        return ' '.join(options)[:100]

    @property
    def score_info(self):
        """Get the individual scores as a dictionary."""
        return self._score_info()

    def _score_info(self):
        """Outputs a total score for this video given a user."""
        scores = VideoSearchEngine.score(
            self.short_text, self.features_as_vector)

        for k, v in zip(VIDEO_FIELDS, self.features_as_vector):
            scores[k] = v

        return scores

    def score_fcn(self):
        """Outputs a total score for this video given a user."""
        info = self._score_info()
        return info['preferences_term'] + info['phrase_term']

    # @property
    # def score(self):
    #     """Returns the score given a user."""
    #     return self.score_fcn()

    def __str__(self):
        is_correct = self.name and not self.wrong_url and self.views
        correct_str = 'VALID' if is_correct else 'INVALID'
        return f"{self.video_id}, {correct_str}"

    def certified_top_raters(self, add_user__username=None):
        """Get certified raters for this video, sorted by number of ratings."""
        qs = UserInformation.objects.filter(user__userpreferences__expertrating__in=self.ratings())
        qs = qs.distinct()
        qs = UserInformation._annotate_is_certified(qs)
        filter_query = Q(_is_certified=True)
        if add_user__username:
            filter_query = filter_query | Q(user__username=add_user__username)
        qs = qs.filter(filter_query)
        qs = qs.annotate(_n_ratings=Count('user__userpreferences__expertrating',
                                          Q(user__userpreferences__expertrating__video_1=self) |
                                          Q(user__userpreferences__expertrating__video_2=self)))
        qs = qs.order_by('-_n_ratings')
        return qs

    @property
    def tournesol_score(self):
        # computed by a query
        return 0.0

    def ratings(self, user=None, only_certified=True):
        """All associated certified ratings."""
        f = Q(video_1=self) | Q(video_2=self)
        if user is not None:
            f = f & Q(user=user)
        qs = ExpertRating.objects.filter(f)
        qs = UserInformation._annotate_is_certified(
            qs, prefix="user__user__userinformation__")
        if only_certified:
            qs = qs.filter(_is_certified=True)
        return qs

    def n_ratings(self, user=None):
        """Number of associated ratings."""
        return self.ratings(user=user).count()

    @property
    def rating_n_ratings(self):
        """Number of ratings."""
        return self.n_ratings()

    @property
    def rating_n_experts(self):
        """Number of experts in ratings."""
        return self.ratings().values('user').distinct().count()


class UserPreferences(models.Model, WithFeatures, WithDynamicFields):
    """One user with preferences."""
    user = models.OneToOneField(
        DjangoUser,
        on_delete=models.CASCADE,
        help_text="DjangoUser that preferences belong to")

    rating_mode = models.CharField(max_length=50, default='enable_all',
                                   help_text="Which sliders and parameters to display"
                                             " on the rating page?",
                                   choices=EnumList('enable_all', 'skip', 'confidence'))

    @staticmethod
    def _create_fields():
        """Adding score fields."""
        for field in VIDEO_FIELDS:
            UserPreferences.add_to_class(
                field,
                models.FloatField(
                    default=0.0,
                    blank=False,
                    help_text=VIDEO_FIELDS_DICT[field],
                    validators=[
                        MinValueValidator(0.0),
                        MaxValueValidator(MAX_RATING)]))

            UserPreferences.add_to_class(
                field + '_enabled',
                models.BooleanField(
                    default=featureIsEnabledByDeFault[field],
                    blank=False,
                    help_text=f"{field} given for ratings"))

    # center ratings around MAX_RATING / 2
    VECTOR_OFFSET = MAX_RATING / 2

    def __str__(self):
        return str(self.user)

    @property
    def username(self):
        """DjangoUser username."""
        return self.user.username


class VideoRatingThankYou(models.Model):
    """Thank you for recommendations."""
    video = models.ForeignKey(Video, on_delete=models.CASCADE,
                              help_text="Video thanked for")
    thanks_from = models.ForeignKey(UserPreferences, on_delete=models.CASCADE,
                                    help_text="Who thanks for the video",
                                    related_name="thanks_from")
    thanks_to = models.ForeignKey(UserPreferences, on_delete=models.CASCADE,
                                  help_text="Who receives the thanks",
                                  related_name="thanks_to")

    class Meta:
        unique_together = ['video', 'thanks_from', 'thanks_to']

    def __str__(self):
        return "%s to %s for %s" % (self.thanks_from, self.thanks_to, self.video)


class VideoRating(models.Model, WithFeatures, WithDynamicFields):
    """Predictions by individual expert models."""
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        help_text="Video being scored")
    user = models.ForeignKey(
        UserPreferences,
        on_delete=models.CASCADE,
        help_text="The expert with scores")

    @staticmethod
    def _create_fields():
        """Adding score fields."""
        for field in VIDEO_FIELDS:
            VideoRating.add_to_class(
                field,
                models.FloatField(
                    default=0,
                    blank=False,
                    help_text=VIDEO_FIELDS_DICT[field]))

        for field in VIDEO_FIELDS:
            # adding the field to user preferences
            VideoRating.add_to_class(
                field + "_uncertainty",
                models.FloatField(
                    default=0,
                    blank=False,
                    help_text=f"Uncertainty for {field}"))

    class Meta:
        unique_together = ['user', 'video']

    def __str__(self):
        return "%s on %s" % (self.user, self.video)


class ExpertRating(models.Model, WithFeatures, WithDynamicFields):
    """Rating given by a user."""

    class Meta:
        unique_together = ['user', 'video_1_2_ids_sorted']
        constraints = [
            models.CheckConstraint(check=~Q(video_1=F('video_2')),
                                   name='videos_cannot_be_equal')
        ]

    user = models.ForeignKey(
        UserPreferences,
        on_delete=models.CASCADE,
        help_text="Expert (user) who left the rating")
    video_1 = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='%(class)s_video_1',
        help_text="Left video to compare")
    video_2 = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='%(class)s_video_2',
        help_text="Right video to compare")
    duration_ms = models.FloatField(
        null=True,
        default=0,
        help_text="Time it took to rate the videos (in milliseconds)")
    datetime_lastedit = models.DateTimeField(
        help_text="Time the rating was edited the last time",
        null=True, blank=True,
    )
    datetime_add = models.DateTimeField(
        auto_now_add=True, help_text="Time the rating was added", null=True, blank=True)
    video_1_2_ids_sorted = computed_property.ComputedCharField(
        compute_from='video_first_second',
        max_length=50,
        default=uuid.uuid1,
        help_text="Sorted pair of video IDs")

    @staticmethod
    def _create_fields():
        """Adding score fields."""
        for field in VIDEO_FIELDS:
            ExpertRating.add_to_class(
                field,
                models.FloatField(
                    blank=True,
                    null=True,
                    default=None,
                    help_text=VIDEO_FIELDS_DICT[field],
                    validators=[
                        MinValueValidator(0.0),
                        MaxValueValidator(MAX_RATING)]))

            ExpertRating.add_to_class(
                field + "_weight",
                models.FloatField(
                    blank=False,
                    default=1,
                    help_text=VIDEO_FIELDS_DICT[field] + " weight",
                    validators=[
                        MinValueValidator(0.0),
                        MaxValueValidator(MAX_FEATURE_WEIGHT)]))

    @property
    def video_first_second(self, videos=None):
        """String representing two video IDs in sorted order."""
        if videos is None:
            videos = [self.video_1, self.video_2]

        videos = [x.id for x in videos]
        a, b = min(videos), max(videos)
        b = max(videos)
        return f"{a}_{b}"

    @staticmethod
    def sample_video_to_rate(username, T=1):
        """Get one video to rate, the more rated before, the less p to choose."""

        # annotation: number of ratings for the video
        annotate_num_ratings = Count(
            'expertrating_video_1__id',
            distinct=True) + Count(
            'expertrating_video_2__id',
            distinct=True)

        class Exp(Func):
            """Exponent in sql."""
            function = 'Exp'

        # annotating with number of ratings
        videos = Video.objects.all().annotate(_num_ratings=annotate_num_ratings)
        score_exp_annotate = Exp(-Value(T,
                                        FloatField()) * F('_num_ratings'),
                                 output_field=FloatField())

        # adding the exponent
        videos = videos.annotate(_score_exp=score_exp_annotate)

        # statistical total sum
        score_exp_sum = videos.aggregate(
            _score_exp_sum=Sum('_score_exp'))['_score_exp_sum']

        # re-computing by dividing by the total sum
        videos = videos.annotate(
            _score_exp_div=F('_score_exp') / score_exp_sum)

        # choosing a random video ID
        ids, ps = zip(*videos.values_list('id', '_score_exp_div'))
        random_video_id = np.random.choice(ids, p=ps)

        return Video.objects.get(id=random_video_id)

    @staticmethod
    def sample_rated_video(username):
        """Get an already rated video, or a random one."""

        # annotation: number of ratings for the video by username
        annotate_num_ratings = Count(
            'expertrating_video_1', filter=Q(
                expertrating_video_1__user__user__username=username)) + Count(
            'expertrating_video_2', filter=Q(
                expertrating_video_2__user__user__username=username))

        # annotating with number of ratings
        videos = Video.objects.all().annotate(_num_ratings=annotate_num_ratings)

        # only selecting those already rated.
        videos = videos.filter(_num_ratings__gt=0)

        if not videos.count():
            logging.warning("No rated videos, returning a random one")
            videos = Video.objects.all()

        # selecting a random ID
        random_id = np.random.choice([x[0] for x in videos.values_list('id')])

        return Video.objects.get(id=random_id)

    @staticmethod
    def sample_video(username, only_rated=False):
        """Sample video based on parameters."""
        if only_rated:
            video = ExpertRating.sample_rated_video(username)
        else:
            video = ExpertRating.sample_video_to_rate(username)
        return video

    def weights_vector(self):
        """How important are the individual scores, according to the rater?"""
        return self._features_as_vector_fcn(suffix="_weight")

    def save(self, *args, **kwargs):
        """Save the object data."""
        if not kwargs.pop('ignore_lastedit', False):
            self.datetime_lastedit = make_aware(datetime.datetime.now())
        if self.pk is None:
            kwargs['force_insert'] = True
        return super().save(*args, **kwargs)

    def __str__(self):
        return "%s [%s/%s]" % (self.user, self.video_1, self.video_2)


class ExpertRatingSliderChanges(models.Model, WithFeatures, WithDynamicFields):
    """Slider values in time for given videos."""

    user = models.ForeignKey(to=UserPreferences, on_delete=models.CASCADE,
                             help_text="Person changing the sliders",
                             null=True)

    video_left = models.ForeignKey(to=Video, on_delete=models.CASCADE,
                                   help_text="Left video", related_name="slider_left",
                                   null=True)
    video_right = models.ForeignKey(to=Video, on_delete=models.CASCADE,
                                    help_text="Right video", related_name="slider_right",
                                    null=True)

    datetime = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the values are added",
        null=True, blank=True,
    )

    duration_ms = models.FloatField(
        null=True,
        default=0,
        help_text="Time from page load to this slider value (in milliseconds)")

    context = models.CharField(choices=EnumList("RATE", "DIS", "INC"),
                               max_length=10, default="RATE",
                               help_text="The page where slider change occurs")

    @staticmethod
    def _create_fields():
        """Adding score fields."""
        for field in VIDEO_FIELDS:
            ExpertRatingSliderChanges.add_to_class(
                field,
                models.FloatField(
                    blank=True,
                    null=True,
                    default=None,
                    help_text=VIDEO_FIELDS_DICT[field],
                    validators=[
                        MinValueValidator(0.0),
                        MaxValueValidator(MAX_RATING)]))

    def __str__(self):
        return "%s [%s] %s/%s at %s" % (self.user, self.context,
                                        self.video_left, self.video_right, self.datetime)


class VideoComment(models.Model, WithDynamicFields):
    """Model for comments on videos."""

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='%(class)s_video',
        help_text="Video to comment")
    user = models.ForeignKey(
        UserPreferences,
        on_delete=models.CASCADE,
        related_name='%(class)s_user',
        help_text="User who left the comment")
    comment = models.TextField(null=False, help_text="Comment body text/html")
    datetime_lastedit = models.DateTimeField(
        auto_now=True, help_text="Time the comment was edited the last time")
    datetime_add = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the comment was added")
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='%(class)s_parent_comment',
        null=True,
        blank=True,
        default=None,
        help_text="The comment that this comment replies to")
    anonymous = models.BooleanField(
        default=False,
        help_text="Do not show author's username")

    red_flag_weight = 10.

    @staticmethod
    def _create_fields():
        """Adding score fields."""
        for field in VIDEO_FIELDS:
            VideoComment.add_to_class(
                field,
                models.BooleanField(
                    null=True,
                    default=False,
                    help_text=VIDEO_FIELDS_DICT[field]))

    @property
    def children(self):
        """Number of children comments."""
        return VideoComment.objects.filter(parent_comment=self).count()

    def __str__(self):
        return "%s on %s: %s" % (
            self.user, self.video, self.comment[:10] + "...")


class VideoCommentMarker(models.Model, WithDynamicFields):
    """Model for comments on videos."""

    class Meta:
        unique_together = ['user', 'comment', 'which']

    comment = models.ForeignKey(
        VideoComment,
        on_delete=models.CASCADE,
        related_name='%(class)s_comment',
        help_text="Comment to mark")
    user = models.ForeignKey(
        UserPreferences,
        on_delete=models.CASCADE,
        related_name='%(class)s_user',
        help_text="User who marks the comment")

    @staticmethod
    def _create_fields():
        """Adding score fields."""
        for field in VideoCommentMarker.MARKER_CHOICES_1:
            @property
            def fcn(self, field=field):
                """Get a sum of markers."""
                which = VideoCommentMarker.MARKER_CHOICES_1to0[field]

                return VideoCommentMarker.objects.filter(
                    comment=self, which=which).count()

            setattr(VideoComment, field, fcn)

    # format: 'which' field value, sum property in VideoComments
    MARKER_CHOICES = [
        ('vote_plus', 'votes_plus'),
        ('vote_minus', 'votes_minus'),
        ('red_flag', 'red_flags'),
    ]

    # to make the usage more convenient
    MARKER_CHOICES_0 = [x[0] for x in MARKER_CHOICES]
    MARKER_CHOICES_1 = [x[1] for x in MARKER_CHOICES]
    MARKER_CHOICES_0to1 = {x[0]: x[1] for x in MARKER_CHOICES}
    MARKER_CHOICES_1to0 = {x[1]: x[0] for x in MARKER_CHOICES}

    # which marker is it?
    which = models.CharField(
        max_length=15,
        choices=MARKER_CHOICES,
    )

    def __str__(self):
        return "%s for %s" % (self.which, self.comment)


class RepresentativeModelUsage(models.Model):
    """Count usage of representative models in search."""
    model = models.ForeignKey(to=UserPreferences, on_delete=models.CASCADE,
                              related_name="model_usage_of", null=False,
                              help_text="Model used for search")
    viewer = models.ForeignKey(to=UserPreferences, on_delete=models.CASCADE,
                               related_name="model_usage_by", null=False,
                               help_text="Person using the model for search")

    class Meta:
        unique_together = ['model', 'viewer']

    def __str__(self):
        return f"{self.model} used by {self.viewer}"


class VideoSelectorSkips(models.Model):
    """Count video being skipped in the Video Selector."""
    user = models.ForeignKey(to=UserPreferences, on_delete=models.CASCADE,
                             related_name="skipped_videos", null=False,
                             help_text="Person who skips the videos")
    video = models.ForeignKey(to=Video, on_delete=models.CASCADE,
                              related_name="skips", null=False,
                              help_text="Video being skipped")
    datetime_add = models.DateTimeField(auto_now_add=True,
                                        help_text="Time the video was skipped",
                                        null=True,
                                        blank=True)

    def __str__(self):
        return f"{self.user}/{self.video}@{self.datetime_add}"


class VideoRatingPrivacy(models.Model):
    """Select whether or not a video rating should be public or private."""
    # one can't simply add an 'is_public' field to the VideoRating models
    # because a corresponding entry might not exist in case if the scores were not yet computed

    # BY-DEFAULT, all ratings are public #370
    DEFAULT_VALUE_IS_PUBLIC = True

    user = models.ForeignKey(to=UserPreferences, on_delete=models.CASCADE,
                             help_text="User who rates videos")
    video = models.ForeignKey(to=Video, on_delete=models.CASCADE,
                              help_text="Video whose rating is either private or public")
    is_public = models.BooleanField(default=False, null=False,
                                    help_text="Should the rating be public?")

    class Meta:
        unique_together = ['user', 'video']

    @staticmethod
    def _annotate_privacy(qs, prefix='video__videoratingprivacy', field_user=F('user'),
                          filter_add=None, default_value=None, annotate_bool=True,
                          annotate_n=False, videorating_field=None):
        """Count number of private/public Privacy database entries.

        By-default, works for the VideoRating model.
        """

        if filter_add is None:
            filter_add = {}

        if field_user is not None:
            filter_add[prefix + '__user'] = field_user

        if default_value is None:
            default_value = VideoRatingPrivacy.DEFAULT_VALUE_IS_PUBLIC

        qs = qs.annotate(
            _n_public_videoratingprivacy=Count(prefix, filter=Q(**{prefix + '__is_public': True,
                                                                   **filter_add}),
                                               distinct=True))
        qs = qs.annotate(
            _n_private_videoratingprivacy=Count(prefix, filter=Q(**{prefix + '__is_public': False,
                                                                    **filter_add}),
                                                distinct=True))

        if annotate_bool:
            if default_value:
                # default value is PUBLIC, therefore public == !(_n_private_videoratingprivacy > 0)
                qs = qs.annotate(_is_public=Case(
                    When(_n_private_videoratingprivacy__gt=0,
                         then=Value(False)),
                    default=Value(True),
                    output_field=BooleanField()))
            else:
                # default value is PRIVATE, therefore public == (_n_public_videoratingprivacy > 0)
                qs = qs.annotate(_is_public=Case(
                    When(_n_public_videoratingprivacy__gt=0,
                         then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()))

        if annotate_n:

            qs = qs.annotate(_n_total=Count(videorating_field,
                                            distinct=True))

            if default_value:
                # default value is PUBLIC -> _n_public = n_total - n_private
                qs = qs.annotate(_n_public=F('_n_total') - F('_n_private_videoratingprivacy'))
                qs = qs.annotate(_n_private=F('_n_private_videoratingprivacy'))
            else:
                # default value is PRIVATE -> _n_private = n_total - n_public
                qs = qs.annotate(_n_private=F('_n_total') - F('_n_public_videoratingprivacy'))
                qs = qs.annotate(_n_public=F('_n_public_videoratingprivacy'))

        return qs

    def __str__(self):
        return f"{self.user}/{self.video}: {'public' if self.is_public else 'private'}"


class VideoRateLater(models.Model):
    """List of videos that a person wants to rate later."""
    user = models.ForeignKey(to=UserPreferences, on_delete=models.CASCADE,
                             help_text="Person who saves the video")
    video = models.ForeignKey(to=Video, on_delete=models.CASCADE,
                              help_text="Video in the rate later list")

    datetime_add = models.DateTimeField(auto_now_add=True,
                                        help_text="Time the video was added to the"
                                                  " rate later list",
                                        null=True,
                                        blank=True)

    class Meta:
        unique_together = ['user', 'video']
        ordering = ['user', '-datetime_add']

    def __str__(self):
        return f"{self.user}/{self.video}@{self.datetime_add}"


# adding dynamic fields
WithDynamicFields.create_all()

# history of edits/changed/additions/deletions/...
register_historical(ExpertRating, excluded_fields=['video_1_2_ids_sorted'])
