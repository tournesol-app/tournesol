"""
Entity score and ratings per poll.
"""

from django.db import models
from django.db.models import Q

from tournesol.models.comparisons import Comparison
from tournesol.models.entity import Entity
from tournesol.models.poll import Poll


class EntityPollRating(models.Model):
    """
    An `EntityPollRating` represents a set of entity related metrics per poll.
    """

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
