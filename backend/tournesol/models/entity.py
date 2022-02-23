"""
Entity and closely related models.
"""

import logging
from datetime import timedelta
from functools import cached_property

import numpy as np
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html
from tqdm.auto import tqdm

from core.models import User
from core.utils.constants import YOUTUBE_VIDEO_ID_REGEX
from tournesol.entities import ENTITY_TYPE_CHOICES, ENTITY_TYPE_NAME_TO_CLASS
from tournesol.entities.video import TYPE_VIDEO
from tournesol.models.tags import Tag
from tournesol.serializers.metadata import VideoMetadata

LANGUAGES = settings.LANGUAGES


class Entity(models.Model):
    """
    A generic entity that can be compared with another one.

    The current model still contains fields from the previous `Video` model.
    These fields are kept as-is for now to ease the refactor of the Tournesol
    app, and will be replaced in the future by the `metadata` JSON field.
    """
    class Meta:
        verbose_name_plural = "entities"

    UID_DELIMITER = ':'
    UID_YT_NAMESPACE = 'yt'

    uid = models.CharField(
        unique=True,
        max_length=144,
        help_text="A unique identifier, build with a namespace and an external id.",
    )

    type = models.CharField(
        max_length=32,
        choices=ENTITY_TYPE_CHOICES,
    )

    metadata = models.JSONField(
        blank=True,
        default=dict
    )
    metadata_timestamp = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp the metadata was uploaded",
    )
    last_metadata_request_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=True,
        help_text="Last time fetch of metadata was attempted",
    )
    add_time = models.DateTimeField(
        null=True, auto_now_add=True, help_text="Time the video was added to Tournesol"
    )

    # TODO: specific to YouTube entities, move it somewhere else
    video_id_regex = RegexValidator(
        YOUTUBE_VIDEO_ID_REGEX, f"Video ID must match {YOUTUBE_VIDEO_ID_REGEX}"
    )

    # TODO: will be replaced by the `uid` field
    video_id = models.CharField(
        max_length=20,
        unique=True,
        help_text=f"Video ID from YouTube URL, matches {YOUTUBE_VIDEO_ID_REGEX}",
        validators=[video_id_regex],
    )

    # TODO
    # the following fields are specific to video entities
    # they will be moved inside the new metadata JSON field

    name = models.CharField(max_length=1000, help_text="Video Title", blank=True)
    description = models.TextField(
        null=True, help_text="Video Description from the web page", blank=True
    )
    duration = models.DurationField(null=True, help_text="Video duration", blank=True)
    language = models.CharField(
        null=True,
        blank=True,
        max_length=10,
        help_text="Language of the video",
        choices=LANGUAGES,
    )
    publication_date = models.DateField(
        null=True, help_text="Video publication date", blank=True
    )
    views = models.BigIntegerField(null=True, help_text="Number of views", blank=True)
    uploader = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        help_text="Name of the channel (uploader)",
    )
    is_unlisted = models.BooleanField(default=False, help_text="Is the video unlisted")
    tags = models.ManyToManyField(Tag, blank=True)

    # TODO
    # the following fields should be moved in a n-n relation with Poll
    rating_n_ratings = models.IntegerField(
        null=False,
        default=0,
        help_text="Total number of pairwise comparisons for this video"
        "from certified contributors",
    )

    # TODO
    # the following fields should be moved in a n-n relation with Poll
    rating_n_contributors = models.IntegerField(
        null=False,
        default=0,
        help_text="Total number of certified contributors who rated the video",
    )

    def update_n_ratings(self):
        from .comparisons import Comparison
        self.rating_n_ratings = Comparison.objects.filter(
            Q(entity_1=self) | Q(entity_2=self)
        ).count()
        self.rating_n_contributors = (
            Comparison.objects.filter(Q(entity_1=self) | Q(entity_2=self))
            .distinct("user")
            .count()
        )
        self.save(update_fields=["rating_n_ratings", "rating_n_contributors"])

    @property
    def entity_cls(self):
        return ENTITY_TYPE_NAME_TO_CLASS[self.type]

    @cached_property
    def inner(self):
        return self.entity_cls(self)

    @property
    def best_text(self, min_len=5):
        """Return description, otherwise title."""
        priorities = [self.description, self.name]

        # going over all priorities
        for priority in priorities:
            # selecting one that exists
            if priority is not None and len(priority) >= min_len:
                return priority
        return None

    @property
    def all_text(self):
        """Return concat of description and title."""
        options = [self.description, self.name]
        options = filter(lambda x: x is not None, options)
        return " ".join(options)

    @property
    def short_text(self):
        """Returns a short string representation of a video"""
        options = [self.name, self.uploader, self.description]
        options = filter(lambda x: x is not None, options)
        return " ".join(options)[:100]

    def __str__(self):
        return f"{self.video_id}"

    def link_to_youtube(self):
        return format_html(
            '<a href="https://youtu.be/{}" target="_blank">Play ▶</a>', self.inner.video_id
        )

    @staticmethod
    def recompute_quantiles():
        """
        WARNING: This implementation is obsolete, and relies on non-existing
        fields "{criteria}_quantile" for videos.
        """
        from .poll import Poll
        CRITERIAS = Poll.default_poll().criterias_list()
        quantiles_by_feature_by_id = {f: {} for f in CRITERIAS}

        # go over all features
        # logging.warning("Computing quantiles...")
        for f in tqdm(CRITERIAS):
            # order by feature (descenting, because using the top quantile)
            qs = Entity.objects.filter(**{f + "__isnull": False}).order_by("-" + f)
            quantiles_f = np.linspace(0.0, 1.0, len(qs))
            for i, v in tqdm(enumerate(qs)):
                quantiles_by_feature_by_id[f][v.id] = quantiles_f[i]

        logging.warning("Writing quantiles...")
        video_objects = []
        # TODO: use batched updates with bulk_update
        for v in tqdm(Entity.objects.all()):
            for f in CRITERIAS:
                setattr(
                    v, f + "_quantile", quantiles_by_feature_by_id[f].get(v.id, None)
                )
            video_objects.append(v)

        Entity.objects.bulk_update(
            video_objects, batch_size=200, fields=[f + "_quantile" for f in CRITERIAS]
        )

    def refresh_youtube_metadata(self, force=False):
        """
        Fetch and update video metadata from Youtube API.

        By default, the request will be executed only if the current metadata
        are older than `VIDEO_METADATA_EXPIRE_SECONDS`.
        The request can be forced with `force=True`.
        """
        from tournesol.utils.api_youtube import VideoNotFound, get_video_metadata

        if (
            not force
            and self.last_metadata_request_at is not None
            and (
                timezone.now() - self.last_metadata_request_at
                < timedelta(seconds=settings.VIDEO_METADATA_EXPIRE_SECONDS)
            )
        ):
            logging.debug(
                "Not refreshing metadata for video %s. Last attempt is too recent at %s",
                self.video_id,
                self.last_metadata_request_at,
            )
            return

        self.last_metadata_request_at = timezone.now()
        self.save(update_fields=["last_metadata_request_at"])
        try:
            metadata = get_video_metadata(self.video_id, compute_language=False)
        except VideoNotFound:
            metadata = {}

        if not metadata:
            return

        for (metadata_key, metadata_value) in metadata.items():
            if metadata_value is not None:
                self.metadata[metadata_key] = metadata_value
        self.metadata_timestamp = timezone.now()
        self.save(update_fields=["metadata", "metadata_timestamp"])

    @classmethod
    def create_from_video_id(cls, video_id):
        from tournesol.utils.api_youtube import VideoNotFound, get_video_metadata
        try:
            extra_data = get_video_metadata(video_id)
        except VideoNotFound:
            raise

        serializer = VideoMetadata(data={
            **extra_data,
            "video_id": video_id,
        })
        if serializer.is_valid():
            metadata = serializer.data
        else:
            raise RuntimeError(f"Unexpected errors in video metadata format: {serializer.errors}")

        return cls.objects.create(
            video_id=video_id,
            type=TYPE_VIDEO,
            uid=f"{cls.UID_YT_NAMESPACE}{cls.UID_DELIMITER}{video_id}",
            metadata=metadata,
            metadata_timestamp=timezone.now(),
        )

    @classmethod
    def get_from_video_id(cls, video_id):
        return cls.objects.get(
            uid=f"{cls.UID_YT_NAMESPACE}{cls.UID_DELIMITER}{video_id}"
        )

    def clean(self):
        # An empty dict is considered as an empty value for JSONField,
        # so blank=True is necessary on "metadata" field.
        # But then, a blank value would break the validation in the admin form
        # as "metadata" is a required non-null value.
        # That's why a default value is set here to handle correctly blank values in forms.
        if self.metadata is None:
            self.metadata = {}


class VideoRateLater(models.Model):
    """List of videos that a person wants to rate later."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="Person who saves the video",
        related_name="videoratelaters",
    )
    video = models.ForeignKey(
        to=Entity,
        on_delete=models.CASCADE,
        help_text="Video in the rate later list",
        related_name="videoratelaters",
    )

    datetime_add = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the video was added to the" " rate later list",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ["user", "video"]
        ordering = ["user", "-datetime_add"]

    def __str__(self):
        return f"{self.user}/{self.video}@{self.datetime_add}"
