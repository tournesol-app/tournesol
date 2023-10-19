"""
The sub-samples API return a sub-sample of entities compared by a user.

A sub-sample is a small finite number of compared entities, ranked by the
individual score computed for the poll's main criterion.
"""
import random

import numpy as np
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

        # Return a sub-sample of the user's ratings, without annotations so as
        # not to affect performance.
        all_ratings = (
            ContributorRating.objects
            .filter(
                poll=poll,
                user=self.request.user,
                criteria_scores__criteria=poll.main_criteria
            )
            .order_by("-criteria_scores__score")
            .values_list("entity_id", flat=True)
        )

        if len(all_ratings) == 0:
            return ContributorRating.objects.none()

        sub_sample_size = min(sub_sample_size, len(all_ratings))
        selected = [random.choice(bucket)  # nosec
                    for bucket in np.array_split(all_ratings, sub_sample_size)]

        # Only the previously selected ratings are retrieved and annotated.
        sub_sample = (
            ContributorRating.objects.annotate_n_comparisons()
            .annotate_last_compared_at()
            .prefetch_related(self.get_prefetch_entity_config())
            .prefetch_related("criteria_scores")
            .filter(
                poll=poll,
                user=self.request.user,
                entity_id__in=selected,
                criteria_scores__criteria=poll.main_criteria
            ).order_by("-criteria_scores__score")
        )

        for idx, item in enumerate(sub_sample):
            item.bucket = idx

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
