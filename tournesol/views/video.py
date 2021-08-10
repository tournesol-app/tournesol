"""
API endpoint to maniuplate videos
"""

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from tournesol.serializers import VideoCriteriaScoreSerializer, VideoSerializer
from tournesol.models import VideoCriteriaScore, Video


class VideoViewSet(viewsets.ModelViewSet):

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = []  # To unlock authentification required

    def retrieve(self, request, *args, **kwargs):
        """
        Get video details and criteria that are related to it
        """

        video = get_object_or_404(Video, video_id=request.data.get("video_id", ""))
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

        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
