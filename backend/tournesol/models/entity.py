"""
Entity and closely related models.
"""

import logging
from collections import defaultdict
from functools import cached_property
from typing import List

import numpy as np
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Prefetch, Q
from django.db.models.expressions import RawSQL
from django.utils import timezone
from django.utils.html import format_html
from tqdm.auto import tqdm

from tournesol.entities import ENTITY_TYPE_CHOICES, ENTITY_TYPE_NAME_TO_CLASS
from tournesol.entities.base import UID_DELIMITER, EntityType
from tournesol.entities.video import TYPE_VIDEO, YOUTUBE_UID_NAMESPACE
from tournesol.models.entity_score import EntityCriteriaScore, ScoreMode
from tournesol.models.rate_later import RateLater
from tournesol.serializers.metadata import VideoMetadata
from tournesol.utils.constants import MEHESTAN_MAX_SCALED_SCORE
from tournesol.utils.video_language import (
    DEFAULT_SEARCH_CONFIG,
    POSTGRES_SEARCH_CONFIGS,
    SEARCH_CONFIG_CHOICES,
    language_to_postgres_config,
)

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

    def filter_with_text_query(self, query: str, languages=None):
        """
        This custom query enables to use the index on 'search_vector' independently of
        the language of the user query.

        The language used to build the 'search_vector' of each entity is stored in a separate
        column 'search_config_name'. However, when calling
        `vector @@ query(search_config_name, text)` Postgres query planner is not smart enough
        to take advantage of this index, although the number of distinct languages is small
        compared to the number of entities. In order to loop over the possible languages and use
        the search index to fetch matching entities without an expensive seqscan, we need to
        explicitly join on 'pg_ts_config' which contains the list of available language
        configurations.
        """
        if languages:
            search_configs = [language_to_postgres_config(lang) for lang in languages]
        else:
            search_configs = POSTGRES_SEARCH_CONFIGS

        return self.alias(
            _matching_query=RawSQL(
                """
                tournesol_entity.id IN (
                    SELECT e.id
                    FROM tournesol_entity e
                    INNER JOIN pg_ts_config c
                        ON c.oid = e.search_config_name::regconfig AND c.cfgname = ANY(%s)
                    WHERE e."search_vector" @@ (plainto_tsquery(oid, %s))
                )
                """,
                # `= ANY(my_list)` is preferred to `IN my_tuple` in this query, as a workaround
                # for a bug in django-debug-toolbar:
                # https://github.com/jazzband/django-debug-toolbar/issues/1482
                (search_configs, query),
            )
        ).filter(_matching_query=True)


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
        indexes = (
            GinIndex(name="search_index", fields=['search_vector']),
        )

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

    search_config_name = models.CharField(
        blank=True,
        default=DEFAULT_SEARCH_CONFIG,
        max_length=32,
        choices=SEARCH_CONFIG_CHOICES,
        help_text="PostgreSQL text search config to use, based on the entity's language",
    )

    search_vector = SearchVectorField(
        editable=False,
        null=True,
        help_text="Indexed words used for the full-text search, that are filtered,"
        " stemmed and weighted according to the language's search config.",
    )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Always refresh the metadata text search vector.

        This would be hard to do with PostgreSQL triggers because
        there are different weights and configs, and the
        format of the metadata can vary with the entity type.
        """
        super().save(force_insert, force_update, using, update_fields)

        # If "metadata" has changed, the indexed search_vector needs to be updated.
        # This condition also avoids infinite loop when calling .save()
        if (update_fields is None) or ("metadata" in update_fields):
            if self.type in ENTITY_TYPE_NAME_TO_CLASS:
                self.entity_cls.update_search_vector(self)

    def update_n_ratings(self):
        from .comparisons import Comparison  # pylint: disable=import-outside-toplevel

        self.rating_n_ratings = Comparison.objects.filter(
            Q(entity_1=self) | Q(entity_2=self)
        ).count()
        self.rating_n_contributors = (
            Comparison.objects.filter(Q(entity_1=self) | Q(entity_2=self))
            .distinct("user")
            .count()
        )
        self.save(update_fields=["rating_n_ratings", "rating_n_contributors"])

    def auto_remove_from_rate_later(self, poll, user) -> None:
        """
        When called, the entity is removed from the user's rate-later list if
        it has been compared at least 4 times.
        """
        from .comparisons import Comparison  # pylint: disable=import-outside-toplevel

        n_comparisons = Comparison.objects.filter(
            poll=poll, user=user
        ).filter(
            Q(entity_1=self) | Q(entity_2=self)
        ).count()

        if n_comparisons >= 4:
            RateLater.objects.filter(
                poll=poll, user=user, entity=self
            ).delete()

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
        min_score_base = -MEHESTAN_MAX_SCALED_SCORE
        max_score_base = MEHESTAN_MAX_SCALED_SCORE

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
            score_range = (min_score_base, max_score_base)
            distribution, bins = np.histogram(np.clip(values, *score_range), range=score_range)

            criteria_distributions.append(CriteriaDistributionScore(
                key, distribution, bins))
        return criteria_distributions

    @staticmethod
    def recompute_quantiles():
        """
        WARNING: This implementation is obsolete, and relies on non-existing
        fields "{criteria}_quantile" for videos.
        """
        from .poll import Poll  # pylint: disable=import-outside-toplevel

        criteria_list = Poll.default_poll().criterias_list()
        quantiles_by_feature_by_id = {criteria: {} for criteria in criteria_list}

        # go over all features
        for criteria in tqdm(criteria_list):
            # order by feature (descenting, because using the top quantile)
            qs = Entity.objects.filter(**{criteria + "__isnull": False}).order_by("-" + criteria)
            quantiles_slicing = np.linspace(0.0, 1.0, len(qs))
            for current_slice, video in tqdm(enumerate(qs)):
                quantiles_by_feature_by_id[criteria][video.id] = quantiles_slicing[current_slice]

        logging.warning("Writing quantiles...")
        video_objects = []
        # TODO: use batched updates with bulk_update
        for entity in tqdm(Entity.objects.all()):
            for criteria in criteria_list:
                setattr(
                    entity,
                    criteria + "_quantile",
                    quantiles_by_feature_by_id[criteria].get(entity.id, None),
                )
            video_objects.append(entity)

        Entity.objects.bulk_update(
            video_objects,
            batch_size=200,
            fields=[criteria + "_quantile" for criteria in criteria_list],
        )

    @classmethod
    def create_from_video_id(cls, video_id):
        # pylint: disable=import-outside-toplevel
        from tournesol.utils.api_youtube import get_video_metadata

        # Returns nothing if no YOUTUBE_API_KEY is not configured.
        # Can also raise VideoNotFound if the video is private or not found by YouTube.
        extra_data = get_video_metadata(video_id)

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

        entity = cls.objects.create(
            type=TYPE_VIDEO,
            uid=f"{YOUTUBE_UID_NAMESPACE}{UID_DELIMITER}{video_id}",
            metadata=metadata,
            metadata_timestamp=timezone.now(),
        )

        return entity

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
        if hasattr(self, "_prefetched_criteria_scores"):
            return list(self._prefetched_criteria_scores)
        return list(self.all_criteria_scores.filter(score_mode=ScoreMode.DEFAULT))


class CriteriaDistributionScore:
    def __init__(self, criteria, distribution, bins):
        self.criteria = criteria
        self.distribution = distribution
        self.bins = bins
