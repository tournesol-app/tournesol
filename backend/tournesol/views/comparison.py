"""
API endpoints to interact with the contributor's comparisons.
"""

from django.db import transaction
from django.db.models import ObjectDoesNotExist, Q
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, generics, mixins, status
from rest_framework.response import Response

from tournesol.models import Comparison, ContributorRating, Entity, Poll
from tournesol.serializers.comparison import ComparisonSerializer, ComparisonUpdateSerializer


class ComparisonApiMixin:
    """A mixin used to factorize behaviours common to all API views."""

    # used to avoid multiple similar database queries in a single HTTP request
    poll_from_url: Poll

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)

        # make the requested poll available at any time in the view
        self.poll_from_url = self.poll_from_kwargs_or_404(kwargs)

    def comparison_already_exists(self, poll_id, request):
        """Return True if the comparison already exist, False instead."""
        try:
            comparison = Comparison.get_comparison(
                request.user,
                poll_id,
                "{}{}{}".format(
                    Entity.UID_YT_NAMESPACE,
                    Entity.UID_DELIMITER,
                    request.data["entity_a"]["video_id"],
                ),
                "{}{}{}".format(
                    Entity.UID_YT_NAMESPACE,
                    Entity.UID_DELIMITER,
                    request.data["entity_b"]["video_id"],
                ),
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

    def poll_from_kwargs_or_404(self, request_kwargs):
        try:
            return Poll.objects.get(name=request_kwargs["poll_name"])
        except ObjectDoesNotExist:
            return self.response_404_poll_doesnt_exist(request_kwargs["poll_name"])

    def response_404_poll_doesnt_exist(self, poll_name):
        return Response(
            {
                "detail": "The requested poll {0} doesn't exist.".format(poll_name),
            },
            status=status.HTTP_404_NOT_FOUND,
        )


class ComparisonListBaseApi(
    ComparisonApiMixin, mixins.ListModelMixin, generics.GenericAPIView
):
    """
    Base class of the ComparisonList API.
    """

    serializer_class = ComparisonSerializer
    queryset = Comparison.objects.none()

    def get_queryset(self):
        """
        Return all or a filtered list of comparisons made by the logged user
        for a given poll.

        Keyword arguments:
        uid -- the entity uid used to filter the results (default None)
        """
        queryset = Comparison.objects.filter(
            poll=self.poll_from_url, user=self.request.user
        ).order_by("-datetime_lastedit")

        if self.kwargs.get("uid"):
            uid = self.kwargs.get("uid")
            queryset = queryset.filter(Q(entity_1__uid=uid) | Q(entity_2__uid=uid))

        return queryset


class ComparisonListApi(mixins.CreateModelMixin, ComparisonListBaseApi):
    """
    List all or a filtered list of comparisons made by the logged user, or
    create a new one.
    """

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["poll"] = self.poll_from_url
        return context

    def get(self, request, *args, **kwargs):
        """
        Retrieve all comparisons made by the logged user, in a given poll.
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create a new comparison associated with the logged user, in a given
        poll.
        """
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        poll = serializer.context["poll"]

        if self.comparison_already_exists(poll.pk, self.request):
            raise exceptions.ValidationError(
                "You've already compared {0} with {1}.".format(
                    self.request.data["entity_a"]["video_id"],
                    self.request.data["entity_b"]["video_id"],
                )
            )
        comparison: Comparison = serializer.save()
        comparison.entity_1.update_n_ratings()
        comparison.entity_1.refresh_youtube_metadata()
        comparison.entity_2.update_n_ratings()
        comparison.entity_2.refresh_youtube_metadata()
        ContributorRating.objects.get_or_create(
            poll=poll, user=self.request.user, entity=comparison.entity_1
        )
        ContributorRating.objects.get_or_create(
            poll=poll, user=self.request.user, entity=comparison.entity_2
        )


class ComparisonListFilteredApi(ComparisonListBaseApi):
    """
    List all or a filtered list of comparisons made by the logged user.
    """

    @extend_schema(operation_id="users_me_comparisons_list_filtered")
    def get(self, request, *args, **kwargs):
        """
        Retrieve a filtered list of comparisons made by the logged user, in
        the given poll.
        """
        return self.list(request, *args, **kwargs)


class ComparisonDetailApi(
    ComparisonApiMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
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
        Return a comparison made by the logged user between two entities, or
        raise HTTP 404 nothing is found.

        If the comparison `uid_a` / `uid_b` is not found, the method will try
        to return the comparison `uid_b` / `uid_a` before raising HTTP 404.

        Query parameters:
        uid_a -- the uid of an entity
        uid_b -- the uid of another entity
        """
        try:
            comparison, reverse = Comparison.get_comparison(
                self.request.user,
                self.poll_from_url.pk,
                self.kwargs["uid_a"],
                self.kwargs["uid_b"],
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
        fields `entity_a` and `entity_b` are not editable anymore once the
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
        context["poll"] = self.poll_from_url
        return context

    def get(self, request, *args, **kwargs):
        """Retrieve a comparison made by the logged user, in the given poll."""
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """Update a comparison made by the logged user, in the given poll"""
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Delete a comparison made by the logged user, in the given poll"""
        return self.destroy(request, *args, **kwargs)
