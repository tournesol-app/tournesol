"""
Entity score and ratings per poll.
"""
from typing import Optional

from django.conf import settings
from django.db import models
from django.db.models import Count, Exists, OuterRef, Q, Subquery, Sum
from django.db.models.functions import Coalesce
from django.utils.functional import cached_property

from tournesol.models.comparisons import Comparison
from tournesol.models.entity import Entity
from tournesol.models.poll import Poll
from tournesol.models.ratings import ContributorRating, ContributorRatingCriteriaScore

UNSAFE_REASON_INSUFFICIENT_SCORE = "insufficient_tournesol_score"
UNSAFE_REASON_INSUFFICIENT_TRUST = "insufficient_trust"

UNSAFE_REASON_MODERATION_ASSOCIATION = "moderation_by_association"
UNSAFE_REASON_MODERATION_CONTRIBUTORS = "moderation_by_contributors"

UNSAFE_REASONS = [
    UNSAFE_REASON_INSUFFICIENT_TRUST,
    UNSAFE_REASON_INSUFFICIENT_SCORE,
    UNSAFE_REASON_MODERATION_ASSOCIATION,
    UNSAFE_REASON_MODERATION_CONTRIBUTORS,
]


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
        default=0.0,
        help_text="Sum of trust scores of the contributors who rated the entity",
    )

    def update_n_ratings(self):
        """
        Refresh the number of comparisons and contributors.
        """
        counts = (
            Comparison.objects
            .filter(Q(entity_1=self.entity) | Q(entity_2=self.entity))
            .filter(poll=self.poll)
            .aggregate(
                n_comparisons=Count("*"),
                n_contributors=Count("user", distinct=True),
            )
        )
        self.n_comparisons = counts["n_comparisons"]
        self.n_contributors = counts["n_contributors"]
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
            sum_trust_scores=Coalesce(
                Subquery(
                    ContributorRating.objects.filter(
                        entity_id=OuterRef("entity_id"),
                        poll=OuterRef("poll"),
                    )
                    .filter(
                        Exists(
                            ContributorRatingCriteriaScore.objects.filter(
                                contributor_rating=OuterRef("id")
                            )
                        )
                    )
                    .values("entity")
                    .annotate(s_t_s=Sum("user__trust_score"))
                    .values("s_t_s")[:1]
                ),
                0.0,
            )
        )

    @staticmethod
    def _bulk_update_sum_trust_score_by_batch(poll, batch_size: int):
        ep_ratings = list(EntityPollRating.objects.filter(poll=poll).filter(
            Exists(ContributorRatingCriteriaScore.objects.filter(
                contributor_rating=OuterRef('entity__contributorvideoratings')
            )),
        ).annotate(
            annotated_sum_trust_scores=Sum("entity__contributorvideoratings__user__trust_score")
        ).only("sum_trust_scores"))
        for ep_rating in ep_ratings:
            ep_rating.sum_trust_scores = ep_rating.annotated_sum_trust_scores or 0.
        EntityPollRating.objects.bulk_update(
            ep_ratings,
            fields=["sum_trust_scores"],
            batch_size=batch_size
        )

    @property
    def is_recommendation_unsafe(self):
        return len(self.unsafe_recommendation_reasons) > 0

    @cached_property
    def unsafe_recommendation_reasons(self):
        # pylint: disable-next=import-outside-toplevel
        from tournesol.models.entity_context import EntityContext

        reasons = []

        if (
            self.tournesol_score is None
            or self.tournesol_score <= settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE
        ):
            reasons.append(UNSAFE_REASON_INSUFFICIENT_SCORE)
        if (
            self.tournesol_score is not None
            and self.sum_trust_scores < settings.RECOMMENDATIONS_MIN_TRUST_SCORES
        ):
            reasons.append(UNSAFE_REASON_INSUFFICIENT_TRUST)

        unsafe, origin = self.poll.entity_has_unsafe_context(self.entity.metadata)
        if unsafe:
            if origin == EntityContext.CONTRIBUTORS:
                reasons.append(UNSAFE_REASON_MODERATION_CONTRIBUTORS)
            else:
                reasons.append(UNSAFE_REASON_MODERATION_ASSOCIATION)

        return reasons
