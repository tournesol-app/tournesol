"""
API endpoint to manipulate contributor ratings
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics

from ..models import ContributorRating
from ..serializers import ContributorRatingSerializer


class ContributorRatingDetail(generics.RetrieveAPIView):
    """
    Retrieve the logged in user's ratings for a specific video
    (computed automatically from the user's comparisons)
    """
    serializer_class = ContributorRatingSerializer

    def get_object(self):
        return get_object_or_404(
            ContributorRating,
            video__video_id=self.kwargs["video_id"],
            user=self.request.user
        )


class ContributorRatingList(generics.ListAPIView):
    """
    Retrieve the logged in user's ratings per video
    (computed automatically from the user's comparisons)
    """
    serializer_class = ContributorRatingSerializer

    def get_queryset(self):
        return ContributorRating.objects.filter(user=self.request.user)
