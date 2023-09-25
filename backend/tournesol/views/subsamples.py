"""
The sub-samples API return a sub-sample of entities compared by a user.

A sub-sample is a small finite number of compared entities, ranked by the
individual score computed for the poll's main criterion.
"""
import random

from django.db.models import Window
from django.db.models.functions import Ntile
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.models import ContributorRating
from tournesol.serializers.subsample import SubSampleSerializer
from tournesol.views.ratings import ContributorRatingQuerysetMixin

# The number of ranked group used to divide the rated entities.
DEFAULT_BUCKET_COUNT = 20


class SubSamplesQuerysetMixin(ContributorRatingQuerysetMixin):
    def get_queryset(self):
        poll = self.poll_from_url

        try:
            sub_sample_size = int(self.request.query_params["ntile"])
        except KeyError:
            sub_sample_size = DEFAULT_BUCKET_COUNT

        qst = (
            ContributorRating.objects.annotate_n_comparisons()
            .annotate_collective_score()
            .annotate_individual_score(poll=poll)
            .prefetch_related(self.get_prefetch_entity_config())
            .filter(
                poll=poll,
                user=self.request.user,
                criteria_scores__criteria=poll.main_criteria
            )
            .annotate(bucket=Window(
                expression=Ntile(sub_sample_size),
                order_by="-criteria_scores__score"
            ))
        )

        sub_sample = []
        rated_entities = len(qst)

        for i in range(min(rated_entities, sub_sample_size)):
            sub_sample.append(
                random.choice([rating for rating in qst if rating.bucket == i + 1])  # nosec
            )

        return sub_sample


class SubSamplesList(SubSamplesQuerysetMixin, generics.ListAPIView):
    """
    Return a sub-sample of entities rated by the logged-in user.

    Entities are ranked by the individual score computed for the poll's
    main criterion, in the descending order.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SubSampleSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ntile",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                default=DEFAULT_BUCKET_COUNT,
                description="Divide the rated entities into `ntile` ranked "
                "buckets, then pick one entity from each bucket.",
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
