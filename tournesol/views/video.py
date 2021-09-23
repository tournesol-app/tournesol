"""
API endpoint to manipulate videos
"""
from collections import OrderedDict

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.response import Response

from ..serializers import VideoSerializerWithCriteria, VideoSerializer
from ..models import Video
from tournesol.utils.api_youtube import youtube_video_details


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = []  # To unlock authentication required

    def retrieve(self, request, pk, *args, **kwargs):
        """
        Get video details and criteria that are related to it
        """
        video = get_object_or_404(Video, video_id=pk)
        video_serialized = VideoSerializerWithCriteria(video)
        return Response(video_serialized.data)

    def list(self, request, *args, **kwargs):
        queryset = Video.objects.all()
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) |
                                       Q(description__icontains=search))

        limit = request.query_params.get('limit')
        if limit and limit.isdigit():
            limit = int(limit)
        else:
            limit = 10

        offset = request.query_params.get('offset')
        if offset and offset.isdigit():
            offset = int(offset)
        else:
            offset = 0

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
        data = []
        for video in queryset.prefetch_related("criteria_scores"):
            total = 0
            for score in video.criteria_scores.all():
                score_query_weight = int(request.query_params.get(score.criteria)) \
                    if request.query_params.get(score.criteria) \
                    and request.query_params.get(score.criteria).isdigit() else 50
                total += score.score * score_query_weight
            video.total = total
            data.append(video)
        data.sort(key=lambda x: x.total, reverse=True)
        count = len(data)
        data = data[offset:offset+limit]
        data_serialised = [VideoSerializerWithCriteria(video).data for video in data]
        return Response(OrderedDict([('count', str(count)), ('results', data_serialised)]))

    def update(self, request, *args, **kwargs):
        return Response('METHOD_NOT_ALLOWED', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response('METHOD_NOT_ALLOWED', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        """
        Add a video to the db if it does not already exist
        """
        if not request.data.get("video_id"):
            return Response('No video_id given', status=status.HTTP_400_BAD_REQUEST)
        if len(request.data.get("video_id")) != 11:
            return Response("video_id given isn't", status=status.HTTP_400_BAD_REQUEST)
        if Video.objects.filter(video_id=request.data["video_id"]):
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
            channel = yt_info["snippet"]["channelTitle"]
            data = {
                "video_id": request.data["video_id"],
                "name": title,
                "description": description,
                "publication_date": published_date,
                "views": nb_views,
                "uploader": channel
            }
            serializer = VideoSerializer(data=data)
        except AssertionError:
            serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
