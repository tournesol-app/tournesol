"""
API endpoint to manipulate contributor ratings
"""

from django.db.models import Func, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import exceptions, generics
from rest_framework.response import Response

from tournesol.models import Comparison, ContributorRating
from tournesol.serializers.rating import (
    ContributorRatingCreateSerializer,
    ContributorRatingSerializer,
    ContributorRatingUpdateAllSerializer,
)


def get_annotated_ratings():
    comparison_counts = (
        Comparison.objects.filter(user=OuterRef("user"))
        .filter(Q(entity_1=OuterRef("entity")) | Q(entity_2=OuterRef("entity")))
        .annotate(count=Func("id", function="Count"))
        .values("count")
    )
    return ContributorRating.objects.annotate(
        n_comparisons=Subquery(comparison_counts)
    ).order_by("-entity__publication_date", "-pk")


@extend_schema_view(
    get=extend_schema(
        description="Retrieve the logged-in user's ratings for a specific video "
        "(computed automatically from the user's comparisons)"
    ),
    put=extend_schema(
        description="Update public / private status of the logged-in user ratings "
        "for a specific video."
    ),
    patch=extend_schema(
        description="Update public / private status of the logged-in user ratings "
        "for a specific video."
    ),
)
class ContributorRatingDetail(generics.RetrieveUpdateAPIView):
    serializer_class = ContributorRatingSerializer

    def get_object(self):
        return get_object_or_404(
            get_annotated_ratings(),
            entity__video_id=self.kwargs["video_id"],
            user=self.request.user,
        )


@extend_schema_view(
    get=extend_schema(
        description="Retrieve the logged in user's ratings per video "
        "(computed automatically from the user's comparisons).",
        parameters=[
            OpenApiParameter("is_public", OpenApiTypes.BOOL, OpenApiParameter.QUERY)
        ],
    ),
    post=extend_schema(
        description="Initialize the rating object for the current user about a "
        "specific video, with optional visibility settings."
    ),
)
class ContributorRatingList(generics.ListCreateAPIView):
    queryset = ContributorRating.objects.none()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ContributorRatingCreateSerializer
        return ContributorRatingSerializer

    def get_queryset(self):
        ratings = (
            get_annotated_ratings()
            .filter(user=self.request.user, n_comparisons__gt=0)
            .select_related("entity")
            .prefetch_related("criteria_scores")
        )
        is_public = self.request.query_params.get("is_public")
        if is_public:
            if is_public == "true":
                ratings = ratings.filter(is_public=True)
            elif is_public == "false":
                ratings = ratings.filter(is_public=False)
            else:
                raise exceptions.ValidationError(
                    "'is_public' query param must be 'true' or 'false'"
                )
        return ratings


class ContributorRatingUpdateAll(generics.GenericAPIView):
    """
    Mark all contributor ratings by current user as public or private.
    """

    serializer_class = ContributorRatingUpdateAllSerializer

    def get_queryset(self):
        return ContributorRating.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset.update(is_public=serializer.validated_data["is_public"])
        return Response(serializer.data)
