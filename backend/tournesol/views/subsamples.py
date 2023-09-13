"""
The sub-samples API return a sub-sample of entities compared by a user.

The compared entities are ordered by score of the poll's main criterion, and
divided into ranked groups called buckets. Each returned entity comes from a
different bucket.
"""

from django.http import JsonResponse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.serializers.subsample import SubSampleSerializer
from tournesol.views import PollScopedViewMixin


class SubSamplesList(PollScopedViewMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubSampleSerializer

    def get_queryset(self):
        # pylint: disable=import-outside-toplevel
        from tournesol.models.ratings import ContributorRating

        return ContributorRating.objects.raw(
            """
            WITH user_ratings AS (
                SELECT
                    contributor_rating.id,
                    contributor_rating.entity_id,

                    NTILE(20) OVER(
                      ORDER BY
                        criteria_score.score DESC
                    ) AS bucket

                FROM tournesol_contributorratingcriteriascore AS criteria_score

                JOIN tournesol_contributorrating AS contributor_rating
                  ON contributor_rating.id = criteria_score.contributor_rating_id

                WHERE criteria_score.criteria = 'largely_recommended'
                  AND contributor_rating.user_id = 1

                ORDER BY random()
            )
            SELECT DISTINCT ON (user_ratings.bucket)
                user_ratings.id,
                user_ratings.entity_id,
                user_ratings.bucket

            FROM user_ratings
            ORDER BY user_ratings.bucket ASC;
            """
        ).prefetch_related("entity")

    def get(self, request, *args, **kwargs):
        sub_samples = self.get_queryset()
        serializer = SubSampleSerializer(sub_samples, many=True)
        return JsonResponse(serializer.data, safe=False)
