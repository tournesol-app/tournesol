"""
API endpoints to interact with the contributor's comparisons
"""

from django.db.models import ObjectDoesNotExist, Q
from django.http import Http404

from rest_framework import generics, mixins, status
from rest_framework.response import Response

from ..models import Comparison, Video
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
                Q(video_1__video_id=video_id) | Q(video_2__video_id=video_id)
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

    def get(self, request, *args, **kwargs):
        """List all comparisons made by the logged user."""
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Create a new comparison, paired with the logged user."""
        if self.comparison_already_exists(request):
            return self.response_400_video_already_exists(request)

        response = self.create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            # Update video_a and video_b ratings
            video_a = Video.objects.get(video_id=request.data['video_a']['video_id'])
            video_a.update_n_ratings()
            video_b = Video.objects.get(video_id=request.data['video_b']['video_id'])
            video_b.update_n_ratings()
        return response


class ComparisonListOnlyApi(ComparisonListBaseApi):
    """
    List all or a filtered list of comparisons made by the logged user.
    """

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
    serializer_class = ComparisonSerializer

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
