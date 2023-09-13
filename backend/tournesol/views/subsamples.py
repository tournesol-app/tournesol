"""
The sub-samples API return a sub-sample of entities compared by a user.

The compared entities are ordered by score of the poll's main criterion, and
divided into ranked groups called buckets. Each returned entity comes from a
different bucket.
"""
import random

from django.db.models import Window
from django.db.models.functions import Ntile
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.models import ContributorRating
from tournesol.serializers.subsample import SubSampleSerializer
from tournesol.views.ratings import ContributorRatingQuerysetMixin


class SubSamplesQuerysetMixin(ContributorRatingQuerysetMixin):
    def get_queryset(self):
        poll = self.poll_from_url

        qst = (
            ContributorRating.objects.annotate_n_comparisons()
            .annotate_collective_score()
            .annotate_individual_score(poll=poll)
            .prefetch_related(self.get_prefetch_entity_config())
            .filter(
                poll=poll,
                user=self.request.user,
                criteria_scores__criteria="largely_recommended"
            )
            .annotate(bucket=Window(expression=Ntile(20), order_by="-criteria_scores__score"))
        )

        # XXX can we use the database to randomly pick a video per bucket instead?
        sub_samples = []
        for i in range(20):
            sub_samples.append(random.choice([rating for rating in qst if rating.bucket == i + 1]))

        return sub_samples


class SubSamplesList(SubSamplesQuerysetMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubSampleSerializer

    def get(self, request, *args, **kwargs):
        sub_samples = self.get_queryset()
        serializer = SubSampleSerializer(sub_samples, many=True)
        return JsonResponse(serializer.data, safe=False)
