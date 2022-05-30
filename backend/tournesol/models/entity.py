"""
Entity and closely related models.
"""

import logging
from collections import defaultdict
from functools import cached_property
from typing import List

import numpy as np
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Prefetch, Q
from django.utils import timezone
from django.utils.html import format_html
from tqdm.auto import tqdm

from core.models import User
from tournesol.entities import ENTITY_TYPE_CHOICES, ENTITY_TYPE_NAME_TO_CLASS
from tournesol.entities.base import UID_DELIMITER, EntityType
from tournesol.entities.video import TYPE_VIDEO, YOUTUBE_UID_NAMESPACE
from tournesol.models.entity_score import EntityCriteriaScore, ScoreMode
from tournesol.serializers.metadata import VideoMetadata

LANGUAGES = settings.LANGUAGES


class EntityQueryset(models.QuerySet):
    def with_prefetched_scores(self, poll_name, mode=ScoreMode.DEFAULT):
        return self.prefetch_related(
            Prefetch(
                "all_criteria_scores",
                queryset=EntityCriteriaScore.objects.filter(
                    poll__name=poll_name,
                    score_mode=mode
                ),
                to_attr="_prefetched_criteria_scores"
            )
        )


class Entity(models.Model):
    """
    A generic entity that can be compared with another one.

    The current model still contains fields from the legacy `Video` model.
    These fields are kept as-is for now to ease the refactor of the Tournesol
    app, and will be moved in the future in a model making a relation between
    a poll and an entity.
    """

    class Meta:
        verbose_name_plural = "entities"

    objects = EntityQueryset.as_manager()

    uid = models.CharField(
        unique=True,
        max_length=144,
        help_text="A unique identifier, build with a namespace and an external id.",
    )

    type = models.CharField(
        max_length=32,
        choices=ENTITY_TYPE_CHOICES,
    )

    metadata = models.JSONField(blank=True, default=dict)
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

    # TODO
    # the following fields should be moved in a n-n relation with Poll
    tournesol_score = models.FloatField(
        null=True,
        blank=True,
        default=None,
        help_text="The aggregated of all criteria for all users in a specific poll.",
    )

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
    def inner(self) -> EntityType:
        """
        An instance of the entity type class related to the current entity.

        For example, to access metadata of the entity, validated by the serializer
        specific to the current entity type, use `self.inner.validated_metadata`.
        """
        return self.entity_cls(self)

    @property
    def video_id(self):
        # A helper for the migration from "video_id" to "uid"
        if self.type != TYPE_VIDEO:
            raise AttributeError("Cannot access 'video_id': this entity is not a video")
        return self.metadata.get("video_id")

    @property
    def best_text(self, min_len=5):
        """Return description, otherwise title."""
        priorities = [self.metadata.get("description"), self.metadata.get("name")]

        # going over all priorities
        for priority in priorities:
            # selecting one that exists
            if priority is not None and len(priority) >= min_len:
                return priority
        return None

    @property
    def all_text(self):
        """Return concat of description and title."""
        options = [self.metadata.get("description"), self.metadata.get("name")]
        options = filter(lambda x: x is not None, options)
        return " ".join(options)

    @property
    def short_text(self):
        """Returns a short string representation of a video"""
        options = [
            self.metadata.get("name"),
            self.metadata.get("uploader"),
            self.metadata.get("description"),
        ]
        options = filter(lambda x: x is not None, options)
        return " ".join(options)[:100]

    def __str__(self):
        return f"{self.uid}"

    def link_to_youtube(self):
        if self.type != TYPE_VIDEO:
            return None
        return format_html(
            '<a href="https://youtu.be/{}" target="_blank">Play ▶</a>', self.video_id
        )

    def criteria_scores_distributions(self, poll):
        """Returns the distribution of criteria score per criteria for the entity"""
        min_score_base = -1.0
        max_score_base = 1.0

        # Fetch data with QuerySet
        contributor_rating_criteria_score_list = [
            list(contributor_rating.criteria_scores.all())
            for contributor_rating in
            self.contributorvideoratings.filter(poll=poll, is_public=True).prefetch_related(
                "criteria_scores"
            )
        ]

        contributor_rating_criteria_score_flatten_list = [
            val for _list in contributor_rating_criteria_score_list for val in _list]

        # Format data into dictionnary
        scores_dict = defaultdict(list)
        for element in contributor_rating_criteria_score_flatten_list:
            scores_dict[element.criteria].append(element.score)

        # Create object
        criteria_distributions = []
        for key, values in scores_dict.items():
            range = (min_score_base, max_score_base)
            distribution, bins = np.histogram(np.clip(values, *range), range=range)

            criteria_distributions.append(CriteriaDistributionScore(
                key, distribution, bins))
        return criteria_distributions

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

    @classmethod
    def create_from_video_id(cls, video_id):
        from tournesol.utils.api_youtube import VideoNotFound, get_video_metadata

        try:
            extra_data = get_video_metadata(video_id)
        except VideoNotFound:
            raise

        serializer = VideoMetadata(
            data={
                **extra_data,
                "video_id": video_id,
            }
        )
        if serializer.is_valid():
            metadata = serializer.data
        else:
            raise RuntimeError(
                f"Unexpected errors in video metadata format: {serializer.errors}"
            )

        return cls.objects.create(
            type=TYPE_VIDEO,
            uid=f"{YOUTUBE_UID_NAMESPACE}{UID_DELIMITER}{video_id}",
            metadata=metadata,
            metadata_timestamp=timezone.now(),
        )

    @classmethod
    def get_from_video_id(cls, video_id):
        return cls.objects.get(uid=f"{YOUTUBE_UID_NAMESPACE}{UID_DELIMITER}{video_id}")

    def clean(self):
        # An empty dict is considered as an empty value for JSONField,
        # so blank=True is necessary on "metadata" field.
        # But then, a blank value would break the validation in the admin form
        # as "metadata" is a required non-null value.
        # That's why a default value is set here to handle correctly blank values in forms.
        if self.metadata is None:
            self.metadata = {}

        if self.type and self.entity_cls.metadata_serializer_class:
            serializer = self.entity_cls.metadata_serializer_class(data=self.metadata)
            if not serializer.is_valid():
                raise ValidationError({"metadata": str(serializer.errors)})
            self.metadata = serializer.data

    @property
    def criteria_scores(self) -> List["EntityCriteriaScore"]:
        from .entity_score import ScoreMode
        if hasattr(self, "_prefetched_criteria_scores"):
            return list(self._prefetched_criteria_scores)
        return list(self.all_criteria_scores.filter(score_mode=ScoreMode.DEFAULT))


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


class CriteriaDistributionScore:
    def __init__(self, criteria, distribution, bins):
        self.criteria = criteria
        self.distribution = distribution
        self.bins = bins
