"""
The sub-samples API return a sub-sample of entities compared by a user.

A sub-sample is a small finite number of compared entities, ranked by the
individual score computed for the poll's main criterion.
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

# The number of ranked group used to divide the rated entities.
NTILE_BUCKETS = 20


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
                criteria_scores__criteria=poll.main_criteria
            )
            .annotate(bucket=Window(
                expression=Ntile(NTILE_BUCKETS),
                order_by="-criteria_scores__score"
            ))
        )

        buckets = len(qst)
        # XXX can we use the database to randomly pick a video per bucket instead?
        sub_samples = []
        for i in range(min(buckets, NTILE_BUCKETS)):
            sub_samples.append(random.choice([rating for rating in qst if rating.bucket == i + 1]))

        return sub_samples


class SubSamplesList(SubSamplesQuerysetMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubSampleSerializer

    def get(self, request, *args, **kwargs):
        """
        Return a sub-sample of entities rated by the logged-in user.

        Entities are ranked by the individual score computed for the poll's
        main criterion, in the descending order.
        """
        sub_samples = self.get_queryset()
        serializer = SubSampleSerializer(sub_samples, many=True)
        return JsonResponse(serializer.data, safe=False)
