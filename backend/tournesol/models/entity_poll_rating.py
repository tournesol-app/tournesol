"""
Entity Poll Rating model
"""

from django.db import models
from django.db.models import Q

from .comparisons import Comparison
from .entity import Entity
from .poll import Poll


class EntityPollRating(models.Model):
    """
    An entity poll rating is a n to n relation between poll and entity to calculate
    entity_score, n_ratings and n_contributors of entity for given poll".
    """

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        help_text="Foreign key to the entity",
        related_name="all_poll_ratings",
    )
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name="ratings",
        default=Poll.default_poll_pk,
    )

    entity_score = models.FloatField(
        null=True,
        blank=True,
        default=None,
        help_text="The aggregated of all criteria for all users in a specific poll.",
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
        self.n_comparisons = Comparison.objects.filter(
            Q(entity_1=self.entity) | Q(entity_2=self.entity)
        ).filter(Q(poll=self.poll)).count()
        self.n_contributors = (
            Comparison.objects
            .filter(Q(entity_1=self) | Q(entity_2=self)).filter(Q(poll=self.poll))
            .distinct("user")
            .count()
        )
        self.save(update_fields=["n_comparisons", "n_contributors"])
