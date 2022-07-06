"""
API endpoints to interact with the contributor's comparisons.
"""

from django.db import transaction
from django.db.models import ObjectDoesNotExist, Q
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, generics, mixins

from ml.mehestan.online_heuristics import update_user_scores
from tournesol.models import Comparison
from tournesol.models.poll import ALGORITHM_MEHESTAN
from tournesol.serializers.comparison import ComparisonSerializer, ComparisonUpdateSerializer
from tournesol.views.mixins.poll import PollScopedViewMixin


class InactivePollError(exceptions.PermissionDenied):
    default_detail = _("This action is not allowed on an inactive poll.")


class ComparisonApiMixin:
    """A mixin used to factorize behaviours common to all API views."""

    def comparison_already_exists(self, poll_id, request):
        """Return True if the comparison already exist, False instead."""
        try:
            comparison = Comparison.get_comparison(
                request.user,
                poll_id,
                request.data["entity_a"]["uid"],
                request.data["entity_b"]["uid"],
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


class ComparisonListBaseApi(
    ComparisonApiMixin,
    PollScopedViewMixin,
    mixins.ListModelMixin,
    generics.GenericAPIView,
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
        if not self.poll_from_url.active:
            raise InactivePollError
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        poll = serializer.context["poll"]

        if self.comparison_already_exists(poll.pk, self.request):
            raise exceptions.ValidationError(
                "You've already compared {0} with {1}.".format(
                    self.request.data["entity_a"]["uid"],
                    self.request.data["entity_b"]["uid"],
                )
            )
        comparison: Comparison = serializer.save()
        comparison.entity_1.update_n_ratings()
        comparison.entity_1.inner.refresh_metadata()
        comparison.entity_1.auto_remove_from_rate_later(self.request.user)
        comparison.entity_2.update_n_ratings()
        comparison.entity_2.inner.refresh_metadata()
        comparison.entity_2.auto_remove_from_rate_later(self.request.user)
        if poll.algorithm == ALGORITHM_MEHESTAN:
            update_user_scores(
                poll,
                user=self.request.user,
                uid_a=self.request.data["entity_a"]["uid"],
                uid_b=self.request.data["entity_b"]["uid"],
                delete_comparison_case=False,
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
    PollScopedViewMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    """
    Retrieve, update or delete a comparison between two entities made by the
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
        by uid swap.
        """
        if self.request.method == "PUT":
            return self.UPDATE_SERIALIZER

        return self.DEFAULT_SERIALIZER

    def get_serializer_context(self):
        context = super(ComparisonDetailApi, self).get_serializer_context()
        context["reverse"] = self.currently_reversed
        context["poll"] = self.poll_from_url
        return context

    def perform_update(self, serializer):
        super().perform_update(serializer)
        poll = self.poll_from_url
        if poll.algorithm == ALGORITHM_MEHESTAN:
            update_user_scores(
                poll,
                user=self.request.user,
                uid_a=self.kwargs["uid_a"],
                uid_b=self.kwargs["uid_b"],
                delete_comparison_case=False,
            )

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        poll = self.poll_from_url
        if poll.algorithm == ALGORITHM_MEHESTAN:
            update_user_scores(
                poll,
                user=self.request.user,
                uid_a=self.kwargs["uid_a"],
                uid_b=self.kwargs["uid_b"],
                delete_comparison_case=True,
            )

    def get(self, request, *args, **kwargs):
        """Retrieve a comparison made by the logged user, in the given poll."""
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """Update a comparison made by the logged user, in the given poll"""
        if not self.poll_from_url.active:
            raise InactivePollError
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Delete a comparison made by the logged user, in the given poll"""
        if not self.poll_from_url.active:
            raise InactivePollError
        return self.destroy(request, *args, **kwargs)
