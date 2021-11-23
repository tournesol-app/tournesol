"""
API endpoint to manipulate contributor ratings
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics, exceptions
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

from ..models import ContributorRating
from ..serializers import ContributorRatingSerializer


class ContributorRatingDetail(generics.RetrieveUpdateAPIView):
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


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter("is_public", OpenApiTypes.BOOL, OpenApiParameter.QUERY)
        ]
    )
)
class ContributorRatingList(generics.ListAPIView):
    """
    Retrieve the logged in user's ratings per video
    (computed automatically from the user's comparisons)
    """
    serializer_class = ContributorRatingSerializer
    queryset = ContributorRating.objects.none()

    def get_queryset(self):
        ratings = ContributorRating.objects.filter(user=self.request.user)
        is_public = self.request.query_params.get('is_public')
        if is_public:
            if is_public == "true":
                ratings = ratings.filter(is_public=True)
            elif is_public == "false":
                ratings = ratings.filter(is_public=False)
            else:
                raise exceptions.ValidationError(
                    "'is_public' query param should be 'true' or 'false'"
                )
        return ratings
