"""
Entity and closely related models.
"""

import logging
from collections import defaultdict
from functools import cached_property
from typing import TYPE_CHECKING, List, Optional
from urllib.parse import urljoin

import numpy as np
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.db.models import Prefetch, Q
from django.db.models.expressions import RawSQL
from django.utils import timezone
from django.utils.html import format_html

from tournesol.entities import ENTITY_TYPE_CHOICES, ENTITY_TYPE_NAME_TO_CLASS
from tournesol.entities.base import UID_DELIMITER, EntityType
from tournesol.entities.video import TYPE_VIDEO, YOUTUBE_UID_NAMESPACE
from tournesol.models.entity_score import EntityCriteriaScore, ScoreMode
from tournesol.models.rate_later import RATE_LATER_AUTO_REMOVE_DEFAULT, RateLater
from tournesol.serializers.metadata import VideoMetadata
from tournesol.utils.constants import MEHESTAN_MAX_SCALED_SCORE
from tournesol.utils.video_language import (
    DEFAULT_SEARCH_CONFIG,
    POSTGRES_SEARCH_CONFIGS,
    SEARCH_CONFIG_CHOICES,
    language_to_postgres_config,
)

if TYPE_CHECKING:
    from tournesol.models.entity_poll_rating import EntityPollRating
    from tournesol.models.ratings import ContributorRating

LANGUAGES = settings.LANGUAGES


class EntityQueryset(models.QuerySet):
    def with_prefetched_scores(self, poll_name, mode=ScoreMode.DEFAULT):
        return self.prefetch_related(
            Prefetch(
                "all_criteria_scores",
                queryset=EntityCriteriaScore.objects.filter(
                    poll__name=poll_name, score_mode=mode
                ),
                to_attr="_prefetched_criteria_scores",
            )
        )

    def with_prefetched_contributor_ratings(self, poll, user, prefetch_criteria_scores=False):
        # pylint: disable=import-outside-toplevel
        from tournesol.models.ratings import ContributorRating

        contributor_ratings = (
            ContributorRating.objects.filter(poll=poll, user=user)
            .annotate_n_comparisons()
        )

        if prefetch_criteria_scores:
            contributor_ratings = contributor_ratings.prefetch_related("criteria_scores")

        return self.prefetch_related(
            Prefetch(
                "contributorvideoratings",
                queryset=contributor_ratings,
                to_attr="_prefetched_contributor_ratings",
            )
        )

    def with_prefetched_poll_ratings(self, poll_name):
        # pylint: disable=import-outside-toplevel
        from tournesol.models.entity_poll_rating import EntityPollRating

        return self.prefetch_related(
            Prefetch(
                "all_poll_ratings",
                queryset=EntityPollRating.objects.prefetch_related(
                    "poll__all_entity_contexts__texts"
                ).filter(
                    poll__name=poll_name,
                ),
                to_attr="single_poll_ratings",
            )
        )

    def filter_safe_for_poll(self, poll):
        exclude_condition = None

        for entity_context in poll.all_entity_contexts.all():
            if not entity_context.enabled or not entity_context.unsafe:
                continue

            expression = None

            for field, value in entity_context.predicate.items():
                kwargs = {f"metadata__{field}": value}
                if expression:
                    expression = expression & Q(**kwargs)
                else:
                    expression = Q(**kwargs)

            if exclude_condition:
                # pylint: disable-next=unsupported-binary-operation
                exclude_condition = exclude_condition | expression
            else:
                exclude_condition = expression

        qst = self.filter(
            all_poll_ratings__poll=poll,
            all_poll_ratings__sum_trust_scores__gte=settings.RECOMMENDATIONS_MIN_TRUST_SCORES,
            all_poll_ratings__tournesol_score__gt=settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE,
        )

        if exclude_condition:
            qst = qst.exclude(exclude_condition)

        return qst

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
        indexes = (GinIndex(name="search_index", fields=["search_vector"]),)

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
        help_text="Last time fetch of metadata was attempted",
    )
    add_time = models.DateTimeField(
        null=True, auto_now_add=True, help_text="Time the video was added to Tournesol"
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

    def update_entity_poll_rating(self, poll):
        """
        Update the related `EntityPollRating` object.

        Keyword arguments:
        poll -- the poll inside which the ratings will be saved
        """
        from .entity_poll_rating import EntityPollRating  # pylint: disable=import-outside-toplevel
        entity_rating, _ = EntityPollRating.objects.get_or_create(
            poll=poll, entity=self
        )
        entity_rating.update_n_ratings()

    def auto_remove_from_rate_later(self, poll, user) -> None:
        """
        When called, the entity is removed from the user's rate-later list if
        it has been compared enough times according to the user's auto remove
        setting.
        """
        from .comparisons import Comparison  # pylint: disable=import-outside-toplevel

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )
        n_comparisons = Comparison.objects.filter(
            poll=poll, user=user
        ).filter(
            Q(entity_1=self) | Q(entity_2=self)
        ).count()

        if n_comparisons >= max_threshold:
            RateLater.objects.filter(poll=poll, user=user, entity=self).delete()

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

    def link_to_tournesol(self):
        if self.type != TYPE_VIDEO:
            return None

        video_uri = urljoin(
            settings.REST_REGISTRATION_MAIN_URL, f"entities/yt:{self.video_id}"
        )
        return format_html('<a href="{}" target="_blank">Play ▶</a>', video_uri)

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
            distribution, bins = np.histogram(np.clip(
                values, *score_range), bins=20, range=score_range)

            criteria_distributions.append(CriteriaDistributionScore(
                key, distribution, bins))
        return criteria_distributions

    @classmethod
    def create_from_video_id(cls, video_id, fetch_metadata=True):
        # pylint: disable=import-outside-toplevel
        from tournesol.utils.api_youtube import VideoNotFound, get_video_metadata

        last_metadata_request_at = None
        if fetch_metadata:
            last_metadata_request_at = timezone.now()
            try:
                extra_data = get_video_metadata(video_id)
            except VideoNotFound:
                logging.warning("Failed to fetch YT metadata about %s", video_id)
                raise
        else:
            extra_data = {}

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

        try:
            return cls.objects.create(
                type=TYPE_VIDEO,
                uid=f"{YOUTUBE_UID_NAMESPACE}{UID_DELIMITER}{video_id}",
                metadata=metadata,
                metadata_timestamp=timezone.now(),
                last_metadata_request_at=last_metadata_request_at,
            )
        except IntegrityError:
            # A concurrent request may have created the video
            return cls.get_from_video_id(video_id)

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

    @property
    def single_poll_rating(self) -> Optional["EntityPollRating"]:
        try:
            if len(self.single_poll_ratings) == 1:
                return self.single_poll_ratings[0]
            return None
        except AttributeError as exc:
            raise RuntimeError(
                "Accessing 'single_poll_rating' requires to initialize a "
                "queryset with `with_prefetched_poll_ratings()`"
            ) from exc

    @property
    def single_contributor_rating(self) -> Optional["ContributorRating"]:
        try:
            if len(self._prefetched_contributor_ratings) == 1:
                return self._prefetched_contributor_ratings[0]
            return None
        except AttributeError as exc:
            raise RuntimeError(
                "Accessing 'single_contributor_rating' requires to initialize a "
                "queryset with `with_prefetched_contributor_ratings()"
            ) from exc

    @property
    def single_poll_entity_contexts(self):
        if self.single_poll_rating is None:
            return []

        poll = self.single_poll_rating.poll
        return poll.get_entity_contexts(self.metadata)


class CriteriaDistributionScore:
    def __init__(self, criteria, distribution, bins):
        self.criteria = criteria
        self.distribution = distribution
        self.bins = bins
