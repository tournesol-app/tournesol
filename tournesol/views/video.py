"""
API endpoint to manipulate videos
"""

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..serializers import VideoCriteriaScoreSerializer, VideoSerializer
from ..models import VideoCriteriaScore, Video
from tournesol.utils.api_youtube import youtube_video_details


class VideoViewSet(viewsets.ModelViewSet):

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = []  # To unlock authentication required

    def retrieve(self, request, pk):
        """
        Get video details and criteria that are related to it
        """

        video = get_object_or_404(Video, video_id=pk)
        video_serialized = VideoSerializer(video)
        video_criterias = VideoCriteriaScore.objects.filter(
            video=video
        )
        criterias_serialized = VideoCriteriaScoreSerializer(video_criterias, many=True)
        return Response(
            (video_serialized.data, criterias_serialized.data),
            status=status.HTTP_200_OK
        )

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
            yt_info = youtube_video_details(request.data["video_id"])["items"][0]
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
