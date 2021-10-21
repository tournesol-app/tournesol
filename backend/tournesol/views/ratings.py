"""
API endpoint to manipulate contributor ratings
"""

from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.response import Response

from ..models import ContributorRating, Video
from ..serializers import ContributorRatingSerializer


class ContributorRatingDetail(generics.GenericAPIView):

    def get(self, request, youtube_video_id):
        """
        Get video details and criteria that are related to it
        """
        video = get_object_or_404(Video, video_id=youtube_video_id)
        ratings = get_object_or_404(ContributorRating, video=video, user=request.user)
        ratings_serialized = ContributorRatingSerializer(ratings)
        return Response(ratings_serialized.data, status=status.HTTP_200_OK)


class ContributorRatingList(generics.ListAPIView):

    queryset = ContributorRating.objects.all()
    serializer_class = ContributorRatingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
