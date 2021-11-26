"""
API endpoint to manipulate videos
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Case, When, Sum, F
from django.conf import settings

from rest_framework import mixins, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers import VideoSerializerWithCriteria, VideoSerializer
from ..models import Video
from tournesol.utils.api_youtube import youtube_video_details
from tournesol.utils.video_language import compute_video_language


class VideoViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    queryset = Video.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = []  # To unlock authentication required

    def get_queryset(self):
        request = self.request
        queryset = self.queryset

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__name__icontains=search)
            )

        date_lte = request.query_params.get('date_lte') \
            if request.query_params.get('date_lte') else ""
        if date_lte:
            try:
                date_lte = timezone.datetime.strptime(date_lte, '%d-%m-%y-%H-%M-%S')
                queryset = queryset.filter(publication_date__lte=date_lte)
            except ValueError:
                pass
        date_gte = request.query_params.get('date_gte') \
            if request.query_params.get('date_gte') else ""
        if date_gte:
            try:
                date_gte = timezone.datetime.strptime(date_gte, '%d-%m-%y-%H-%M-%S')
                queryset = queryset.filter(publication_date__gte=date_gte)
            except ValueError:
                pass
        language = request.query_params.get('language') \
            if request.query_params.get('language') else ""
        queryset = queryset.filter(language=language) if language else queryset

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

    def retrieve(self, request, pk):
        """
        Get video details and criteria that are related to it
        """
        video = get_object_or_404(Video, video_id=pk)
        video_serialized = VideoSerializerWithCriteria(video)
        return Response(video_serialized.data)

    def create(self, request, *args, **kwargs):
        """
        Add a video to the db if it does not already exist
        """
        video_id = request.data.get("video_id")
        if not video_id:
            return Response('No video_id given', status=status.HTTP_400_BAD_REQUEST)
        if len(video_id) != 11:
            return Response("video_id is not valid", status=status.HTTP_400_BAD_REQUEST)
        if Video.objects.filter(video_id=video_id):
            Response(
                "The video with the id : {id} is already registered".format(
                    id=request.data["video_id"]),
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            yt_response = youtube_video_details(request.data["video_id"])
            yt_items = yt_response.get("items", [])
            if len(yt_items) == 0:
                return Response(
                    "The video has not been found. `video_id` may be incorrect.",
                    status=status.HTTP_404_NOT_FOUND
                )
            yt_info = yt_items[0]
            title = yt_info["snippet"]["title"]
            nb_views = yt_info["statistics"]["viewCount"]
            published_date = str(yt_info["snippet"]["publishedAt"])
            published_date = published_date.split("T")[0]
            # we could truncate description to spare some space
            description = str(yt_info["snippet"]["description"])
            uploader = yt_info["snippet"]["channelTitle"]
            language = compute_video_language(uploader, title, description)
            #  if video has no tags, te field doesn't appear on response
            tags = yt_info["snippet"].get("tags", [])
            extra_data = {
                "name": title,
                "description": description,
                "publication_date": published_date,
                "views": nb_views,
                "uploader": uploader,
                "language": language,
                "tags": tags,
            }
        except AssertionError:
            extra_data = {"tags": []}
        serializer = VideoSerializer(data={"video_id": video_id})
        if serializer.is_valid():
            serializer.save(**extra_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
