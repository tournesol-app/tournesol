"""
API endpoints to interact with the contributor's comparisons
"""

from django.db import transaction
from django.db.models import ObjectDoesNotExist, Q
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, generics, mixins, status
from rest_framework.response import Response

from ..models import Comparison, ContributorRating, Poll
from ..serializers import ComparisonSerializer, ComparisonUpdateSerializer


class ComparisonApiMixin:
    """
    A mixin providing several common tools to all comparison API views.
    """

    def comparison_already_exists(self, request):
        """Return True if the comparison already exist, False instead."""
        try:
            comparison = Comparison.get_comparison(
                request.user, request.data['video_a']['video_id'],
                request.data['video_b']['video_id']
            )
        # if one field is missing, do not raise error yet and let django rest
        # framework checks the request integrity
        except KeyError:
            return False
        except ObjectDoesNotExist:
            return False

        if comparison:
            return True
        else:
            return False

    def response_400_video_already_exists(self, request):
        return Response(
            {
                "detail": "You've already compared {0} with {1}.".format(
                    request.data['video_a']['video_id'],
                    request.data['video_b']['video_id']
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ComparisonListBaseApi(ComparisonApiMixin,
                            mixins.ListModelMixin,
                            generics.GenericAPIView):
    """
    Base class of the ComparisonList API.
    """
    serializer_class = ComparisonSerializer
    queryset = Comparison.objects.none()

    def get_queryset(self):
        """
        Return all or a filtered list of comparisons made by the logged user.

        Keyword arguments:
        video_id -- the video_id used to filter the results (default None)
        """
        queryset = Comparison.objects.filter(user=self.request.user).order_by('-datetime_lastedit')

        if self.kwargs.get("video_id"):
            video_id = self.kwargs.get("video_id")
            queryset = queryset.filter(
                Q(entity_1__video_id=video_id) | Q(entity_2__video_id=video_id)
            )

        return queryset


class ComparisonListApi(
    mixins.CreateModelMixin,
    ComparisonListBaseApi
):
    """
    List all or a filtered list of comparisons made by the logged user, or
    create a new one.
    """
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["poll"] = Poll.default_poll()
        return context

    def get(self, request, *args, **kwargs):
        """List all comparisons made by the logged user."""
        return self.list(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        if self.comparison_already_exists(self.request):
            raise exceptions.ValidationError(
                "You've already compared {0} with {1}.".format(
                    self.request.data['video_a']['video_id'],
                    self.request.data['video_b']['video_id']
                )
            )
        comparison: Comparison = serializer.save()
        comparison.entity_1.update_n_ratings()
        comparison.entity_1.refresh_youtube_metadata()
        comparison.entity_2.update_n_ratings()
        comparison.entity_2.refresh_youtube_metadata()
        ContributorRating.objects.get_or_create(user=self.request.user, entity=comparison.entity_1)
        ContributorRating.objects.get_or_create(user=self.request.user, entity=comparison.entity_2)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ComparisonListFilteredApi(ComparisonListBaseApi):
    """
    List all or a filtered list of comparisons made by the logged user.
    """

    @extend_schema(operation_id='users_me_comparisons_list_filtered')
    def get(self, request, *args, **kwargs):
        """List all comparisons made by the logged user."""
        return self.list(request, *args, **kwargs)


class ComparisonDetailApi(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          generics.GenericAPIView):
    """
    Retrieve, update or delete a comparison between two videos made by the
    logged user.
    """
    DEFAULT_SERIALIZER = ComparisonSerializer
    UPDATE_SERIALIZER = ComparisonUpdateSerializer

    currently_reversed = False

    def _select_serialization(self, straight=True):
        if straight:
            self.currently_reversed = False
        else:
            self.currently_reversed = True

    def get_object(self):
        """
        Return a comparison made by the logged user between two videos, or
        raise HTTP 404 nothing is found.

        If the comparison `video_id_a` / `video_id_b` is not found, the
        method will try to return the comparison `video_id_b` / `video_id_a`
        before raising HTTP 404.

        Query parameters:
        video_id_a -- the video_id of a video
        video_id_b -- the video_id of an other video
        """
        try:
            comparison, reverse = Comparison.get_comparison(
                self.request.user, self.kwargs['video_id_a'],
                self.kwargs['video_id_b']
            )
        except ObjectDoesNotExist:
            raise Http404

        if reverse:
            self._select_serialization(straight=False)

        return comparison

    def get_serializer_class(self):
        """
        Determine the appropriate serializer based on the request's method.

        Updating a comparison requires a different serializer because the
        fields `video_a` and `video_b` are not editable anymore once the
        comparison has been created. Discarding those two fields ensures
        their immutability and thus prevent the falsification of comparisons
        by video id swap.
        """
        if self.request.method == "PUT":
            return self.UPDATE_SERIALIZER

        return self.DEFAULT_SERIALIZER

    def get_serializer_context(self):
        context = super(ComparisonDetailApi, self).get_serializer_context()
        context["reverse"] = self.currently_reversed
        context["poll"] = Poll.default_poll()
        return context

    def get(self, request, *args, **kwargs):
        """Retrieve a comparison made by the logged user."""
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """Update a comparison made by the logged user."""
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Delete a comparison made by the logged user."""
        return self.destroy(request, *args, **kwargs)
