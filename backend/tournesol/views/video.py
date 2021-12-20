"""
API endpoint to manipulate videos
"""
import re
import isodate

from django.utils import timezone, dateparse
from django.db.models import Q, Case, When, Sum, F
from django.conf import settings

from rest_framework import mixins
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import ValidationError, NotFound
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from drf_spectacular.types import OpenApiTypes

from ..serializers import VideoSerializerWithCriteria, VideoSerializer
from ..models import Video
from tournesol.utils.api_youtube import youtube_video_details
from tournesol.utils.video_language import compute_video_language


@extend_schema_view(
    create=extend_schema(
        description="Add a video to the db if it does not already exist."
    ),
    retrieve=extend_schema(
        description="Retrieve details about a single video."
    ),
    list=extend_schema(
        description="Retrieve a list of recommended videos, sorted by decreasing total score.",
        parameters=[
            OpenApiParameter("search"),
            OpenApiParameter("languages", description="Accepted languages separated by commas (e.g. 'en,fr,de')."
                                                      "If empty, accept all languages"),
            OpenApiParameter(
                "date_lte",
                OpenApiTypes.DATETIME,
                description="Return videos published **before** this date.  \n"
                "Accepted formats: ISO 8601 datetime (e.g `2021-12-01T12:45:00`) "
                "or legacy: `dd-mm-yy-hh-mm-ss`."
            ),
            OpenApiParameter(
                "date_gte",
                OpenApiTypes.DATETIME,
                description="Return videos published **after** this date.  \n"
                "Accepted formats: ISO 8601 datetime (e.g `2021-12-01T12:45:00`) "
                "or legacy: `dd-mm-yy-hh-mm-ss`."
            ),
            *[
                OpenApiParameter(
                    crit,
                    OpenApiTypes.INT,
                    description=f"Weight for criteria '{crit}', between 0 and 100"
                )
                for crit in settings.CRITERIAS
            ],
        ],
    )
)
class VideoViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    queryset = Video.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = []  # To unlock authentication required
    lookup_field = "video_id"

    def parse_datetime(self, value: str):
        """
        Parse ISO datetime from query string.
        Also accepts legacy format 'DD-MM-YY-HH-MM-SS'
        """
        if re.match(r'^\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}$', value):
            return timezone.datetime.strptime(value, '%d-%m-%y-%H-%M-%S')
        parsed = dateparse.parse_datetime(value)
        if parsed is None:
            raise ValueError(f'Failed to parse "{value}" as datetime')
        return parsed

    def get_queryset(self):
        if self.action != "list":
            return self.queryset

        request = self.request
        queryset = self.queryset

        search = request.query_params.get('search')
        if search:
            # Filtering in a nested queryset is necessary here, to be able to annotate
            # each video without duplicated scores, due to the m2m field 'tags'.
            queryset = queryset.filter(pk__in=Video.objects.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__name__icontains=search)
            ))

        date_lte = request.query_params.get('date_lte') or ""
        if date_lte:
            try:
                date_lte = self.parse_datetime(date_lte)
                queryset = queryset.filter(publication_date__lte=date_lte)
            except ValueError:
                raise ValidationError('"date_lte" is an invalid datetime.')
        date_gte = request.query_params.get('date_gte') or ""
        if date_gte:
            try:
                date_gte = self.parse_datetime(date_gte)
                queryset = queryset.filter(publication_date__gte=date_gte)
            except ValueError:
                raise ValidationError('"date_gte" is an invalid datetime')

        languages = request.query_params.get('languages').split(",") \
            if request.query_params.get('languages') else []
        queryset = queryset.filter(language__in=languages) if languages else queryset

        criteria_cases = [
            When(
                criteria_scores__criteria=crit,
                then=int(
                    request.query_params.get(crit)
                    if request.query_params.get(crit)
                    and request.query_params.get(crit).isdigit()
                    else 50
                ),
            )
            for crit in settings.CRITERIAS
        ]
        criteria_weight = Case(*criteria_cases, default=0)
        queryset = (
            queryset.annotate(
                total_score=Sum(F("criteria_scores__score") * criteria_weight)
            )
            .filter(total_score__gt=0)
            .order_by("-total_score")
        )
        return queryset.prefetch_related("criteria_scores")

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return VideoSerializerWithCriteria
        return VideoSerializer

    def perform_create(self, serializer):
        video_id = serializer.validated_data["video_id"]
        try:
            yt_response = youtube_video_details(video_id)
            yt_items = yt_response.get("items", [])
            if len(yt_items) == 0:
                raise NotFound("The video has not been found. `video_id` may be incorrect.")
            yt_info = yt_items[0]
            title = yt_info["snippet"]["title"]
            nb_views = yt_info.get("statistics", {}).get("viewCount")
            published_date = str(yt_info["snippet"]["publishedAt"])
            published_date = published_date.split("T")[0]
            # we could truncate description to spare some space
            description = str(yt_info["snippet"]["description"])
            uploader = yt_info["snippet"]["channelTitle"]
            language = compute_video_language(uploader, title, description)
            #  if video has no tags, te field doesn't appear on response
            tags = yt_info["snippet"].get("tags", [])
            duration = isodate.parse_duration(yt_info["contentDetails"]["duration"])
            extra_data = {
                "name": title,
                "description": description,
                "publication_date": published_date,
                "views": nb_views,
                "uploader": uploader,
                "language": language,
                "tags": tags,
                "duration": duration,
            }
        except AssertionError:
            extra_data = {"tags": []}
        serializer.save(**extra_data)
