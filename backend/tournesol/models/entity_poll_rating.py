"""
Entity score and ratings per poll.
"""
from typing import Optional

from django.db import models
from django.db.models import OuterRef, Q, Subquery, Sum
from django.db.models.functions import Coalesce

from tournesol.models.comparisons import Comparison
from tournesol.models.entity import Entity
from tournesol.models.poll import Poll


class EntityPollRating(models.Model):
    """
    An `EntityPollRating` represents a set of entity related metrics per poll.
    """

    class Meta:
        unique_together = ["poll", "entity"]

    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name="all_entity_ratings",
        default=Poll.default_poll_pk,
    )

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="all_poll_ratings",
    )

    tournesol_score = models.FloatField(
        null=True,
        blank=True,
        default=None,
        help_text="The aggregated score of the main criterion for all users, in a specific poll.",
    )

    n_comparisons = models.IntegerField(
        null=False,
        default=0,
        help_text="Total number of pairwise comparisons for this entity"
        "from certified contributors",
    )

    n_contributors = models.IntegerField(
        null=False,
        default=0,
        help_text="Total number of certified contributors who rated the entity",
    )

    sum_trust_scores = models.FloatField(
        null=False,
        default=0.,
        help_text="Sum of trust scores of the contributors who rated the entity",
    )

    def update_n_ratings(self):
        """
        Refresh the number of comparisons and contributors.
        """
        self.n_comparisons = (
            Comparison.objects.filter(Q(entity_1=self.entity) | Q(entity_2=self.entity))
            .filter(Q(poll=self.poll))
            .count()
        )

        self.n_contributors = (
            Comparison.objects.filter(Q(entity_1=self.entity) | Q(entity_2=self.entity))
            .filter(Q(poll=self.poll))
            .distinct("user")
            .count()
        )

        self.save(update_fields=["n_comparisons", "n_contributors"])

    @staticmethod
    def bulk_update_sum_trust_scores(poll: Poll, batch_size: Optional[int] = 4000):
        if batch_size is None:
            EntityPollRating._bulk_update_sum_trust_score(poll)
        else:
            EntityPollRating._bulk_update_sum_trust_score_by_batch(poll, batch_size)

    @staticmethod
    def _bulk_update_sum_trust_score(poll):
        EntityPollRating.objects.filter(poll=poll).update(
            sum_trust_scores=Coalesce(Subquery(
                Entity.objects.filter(
                    id=OuterRef('entity_id'),
                    contributorvideoratings__poll=OuterRef('poll'),
                ).annotate(
                    s_t_s=Sum("contributorvideoratings__user__trust_score")
                ).values("s_t_s")[:1]
            ), 0.)
        )

    @staticmethod
    def _bulk_update_sum_trust_score_by_batch(poll, batch_size: int):
        ep_ratings = list(EntityPollRating.objects.filter(poll=poll).annotate(
            annotated_sum_trust_scores=Sum("entity__contributorvideoratings__user__trust_score")
        ).only("sum_trust_scores"))
        for ep_rating in ep_ratings:
            ep_rating.sum_trust_scores = ep_rating.annotated_sum_trust_scores or 0.
        EntityPollRating.objects.bulk_update(
            ep_ratings,
            fields=["sum_trust_scores"],
            batch_size=batch_size
        )
