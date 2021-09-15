"""
API endpoint to manipulate contributor ratings
"""

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import ContributorRating, Video
from ..serializers import ContributorRatingSerializer


class ContributorRatingViewSet(viewsets.ModelViewSet):

    queryset = ContributorRating.objects.all()
    serializer_class = ContributorRatingSerializer

    def retrieve(self, request, pk):
        """
        Get video details and criteria that are related to it
        """

        video = get_object_or_404(Video, video_id=pk)
        ratings = get_object_or_404(ContributorRating, video=video, user=request.user)
        ratings_serialized = ContributorRatingSerializer(ratings)
        return Response(ratings_serialized.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):

        self.queryset.filter(user=request.user)
        ratings_serialized = ContributorRatingSerializer(self.queryset, many=True)
        return Response(ratings_serialized.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return Response('METHOD_NOT_ALLOWED', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response('METHOD_NOT_ALLOWED', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response('METHOD_NOT_ALLOWED', status=status.HTTP_405_METHOD_NOT_ALLOWED)
