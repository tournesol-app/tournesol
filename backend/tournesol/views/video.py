"""
API endpoint to manipulate videos
"""
import re

from django.conf import settings
from django.db.models import Case, F, Sum, When
from django.shortcuts import get_object_or_404
from django.utils import dateparse, timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import GenericViewSet

from tournesol.entities import VideoEntity
from tournesol.entities.base import UID_DELIMITER
from tournesol.entities.video import TYPE_VIDEO, YOUTUBE_UID_NAMESPACE
from tournesol.models import Entity
from tournesol.models.entity_score import ScoreMode
from tournesol.models.poll import DEFAULT_POLL_NAME
from tournesol.serializers.entity import VideoSerializer, VideoSerializerWithCriteria
from tournesol.throttling import (
    BurstAnonRateThrottle,
    BurstUserRateThrottle,
    PostScopeRateThrottle,
    SustainedAnonRateThrottle,
    SustainedUserRateThrottle,
)


@extend_schema_view(
    create=extend_schema(
        description="Add a video to the db if it does not already exist."
    ),
    retrieve=extend_schema(description="Retrieve details about a single video."),
    list=extend_schema(
        description="Retrieve a list of recommended videos, sorted by decreasing total score.",
        parameters=[
            OpenApiParameter("search"),
            OpenApiParameter(
                "language",
                description="Accepted languages separated by commas "
                "(e.g. 'en,fr,de'). If empty, accept all languages.",
            ),
            OpenApiParameter("uploader"),
            OpenApiParameter(
                "date_lte",
                OpenApiTypes.DATETIME,
                description="Return videos published **before** this date.  \n"
                "Accepted formats: ISO 8601 datetime (e.g `2021-12-01T12:45:00`) "
                "or legacy: `dd-mm-yy-hh-mm-ss`.",
            ),
            OpenApiParameter(
                "date_gte",
                OpenApiTypes.DATETIME,
                description="Return videos published **after** this date.  \n"
                "Accepted formats: ISO 8601 datetime (e.g `2021-12-01T12:45:00`) "
                "or legacy: `dd-mm-yy-hh-mm-ss`.",
            ),
            OpenApiParameter(
                "unsafe",
                OpenApiTypes.BOOL,
                description="If true, videos considered as unsafe recommendations because of a "
                "low score or due to too few contributions will be included.",
            ),
            *[
                OpenApiParameter(
                    crit,
                    OpenApiTypes.INT,
                    description=f"Weight for criteria '{crit}', between 0 and 100",
                )
                for crit in settings.LEGACY_CRITERIAS
            ],
        ],
    ),
)
class VideoViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """Obsolete view for video recommendations."""
    queryset = Entity.objects.filter(type=TYPE_VIDEO)
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    throttle_classes = [
        PostScopeRateThrottle,
        BurstAnonRateThrottle,
        BurstUserRateThrottle,
        SustainedAnonRateThrottle,
        SustainedUserRateThrottle,
    ]
    throttle_scope = "api_video_post"

    lookup_field = "video_id"

    def parse_datetime(self, value: str):
        """
        Parse ISO datetime from query string.
        Also accepts legacy format 'DD-MM-YY-HH-MM-SS'
        """
        if re.match(r"^\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}$", value):
            return timezone.datetime.strptime(value, "%d-%m-%y-%H-%M-%S")
        parsed = dateparse.parse_datetime(value)
        if parsed is None:
            raise ValueError(f'Failed to parse "{value}" as datetime')
        return parsed

    def get_object(self):
        obj = get_object_or_404(
            self.queryset,
            uid=f'{YOUTUBE_UID_NAMESPACE}{UID_DELIMITER}{self.kwargs["video_id"]}',
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        if self.action != "list":
            return self.queryset

        request = self.request
        queryset = self.queryset

        uploader = request.query_params.get("uploader")
        if uploader:
            queryset = queryset.filter(metadata__uploader=uploader)

        search = request.query_params.get("search")
        if search:
            queryset = VideoEntity.filter_search(queryset, search)

        date_lte = request.query_params.get("date_lte") or ""
        if date_lte:
            try:
                date_lte = self.parse_datetime(date_lte)
                queryset = VideoEntity.filter_date_lte(queryset, date_lte)
            except ValueError as error:
                raise ValidationError('"date_lte" is an invalid datetime.') from error
        date_gte = request.query_params.get("date_gte") or ""
        if date_gte:
            try:
                date_gte = self.parse_datetime(date_gte)
                queryset = VideoEntity.filter_date_gte(queryset, date_gte)
            except ValueError as error:
                raise ValidationError('"date_gte" is an invalid datetime') from error

        language = request.query_params.get("language")
        if language:
            queryset = queryset.filter(metadata__language__in=language.split(","))

        criteria_cases = [
            When(
                all_criteria_scores__criteria=crit,
                then=int(
                    request.query_params.get(crit)
                    if request.query_params.get(crit)
                    and request.query_params.get(crit).isdigit()
                    else 50
                ),
            )
            for crit in settings.LEGACY_CRITERIAS
        ]
        criteria_weight = Case(*criteria_cases, default=0)

        queryset = (
            queryset
            .filter(all_criteria_scores__score_mode=ScoreMode.DEFAULT)
            .annotate(
                total_score=Sum(F("all_criteria_scores__score") * criteria_weight)
            ).filter(total_score__isnull=False)
        )

        show_unsafe = request.query_params.get("unsafe") == "true"

        if not show_unsafe:
            queryset = queryset.filter(
                rating_n_contributors__gte=settings.RECOMMENDATIONS_MIN_CONTRIBUTORS
            ).filter(tournesol_score__gt=0)
        return (
            queryset
            .with_prefetched_scores(poll_name=DEFAULT_POLL_NAME)
            .order_by("-total_score", "-metadata__publication_date")
        )

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return VideoSerializerWithCriteria
        return VideoSerializer
