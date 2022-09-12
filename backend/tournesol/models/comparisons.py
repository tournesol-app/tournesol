"""
Models for Tournesol's main functions related to contributor's comparisons
"""

import uuid

import computed_property
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, ObjectDoesNotExist, Q

from core.models import User
from tournesol.utils.constants import COMPARISON_MAX

from .poll import Poll


class Comparison(models.Model):
    """Rating given by a user."""

    class Meta:
        unique_together = ["user", "poll", "entity_1_2_ids_sorted"]
        constraints = [
            models.CheckConstraint(
                check=~Q(entity_1=F("entity_2")), name="videos_cannot_be_equal"
            )
        ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comparisons",
        help_text="Contributor (user) who left the rating",
    )
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name="comparisons"
    )
    entity_1 = models.ForeignKey(
        'Entity',
        on_delete=models.CASCADE,
        related_name="comparisons_entity_1",
        help_text="Left entity to compare",
    )
    entity_2 = models.ForeignKey(
        'Entity',
        on_delete=models.CASCADE,
        related_name="comparisons_entity_2",
        help_text="Right entity to compare",
    )
    duration_ms = models.FloatField(
        null=True,
        default=0,
        help_text="Time it took to rate the videos (in milliseconds)",
    )
    datetime_lastedit = models.DateTimeField(
        help_text="Time the comparison was edited the last time",
        null=True,
        blank=True,
        auto_now=True,
    )
    datetime_add = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the comparison was added",
        null=True,
        blank=True,
    )
    entity_1_2_ids_sorted = computed_property.ComputedCharField(
        compute_from="entity_first_second",
        max_length=50,
        default=uuid.uuid1,
        help_text="Sorted pair of video IDs",
    )

    @property
    def entity_first_second(self):
        """String representing two entity PKs in sorted order."""
        entity_1, entity_2 = sorted([self.entity_1_id, self.entity_2_id])
        return f"{entity_1}_{entity_2}"

    @staticmethod
    def get_comparison(user, poll_id, uid_a, uid_b):
        """
        Return a tuple with the user's comparison between two videos in the
        given poll, and True is the comparison is made in the reverse way,
        False instead.

        Raise django.db.model.ObjectDoesNotExist if no comparison is found.
        """
        try:
            comparison = Comparison.objects.get(
                user=user,
                poll_id=poll_id,
                entity_1__uid=uid_a,
                entity_2__uid=uid_b,
            )
        except ObjectDoesNotExist:
            pass
        else:
            return comparison, False

        comparison = Comparison.objects.get(
            user=user,
            poll_id=poll_id,
            entity_1__uid=uid_b,
            entity_2__uid=uid_a,
        )

        return comparison, True

    def __str__(self):
        return f"{self.user} [{self.entity_1}/{self.entity_2}]"


class ComparisonCriteriaScore(models.Model):
    """Scores per criteria for comparisons submitted by contributors"""

    comparison = models.ForeignKey(
        to=Comparison,
        help_text="Foreign key to the contributor's comparison",
        related_name="criteria_scores",
        on_delete=models.CASCADE,
    )
    criteria = models.TextField(
        db_index=True,
        max_length=32,
        help_text="Name of the criteria",
    )
    score = models.FloatField(
        help_text="Score for the given comparison",
        validators=[MinValueValidator(-COMPARISON_MAX), MaxValueValidator(COMPARISON_MAX)],
    )
    # TODO: ask Lê if weights should be in a certain range (maybe always > 0)
    # and add validation if required
    weight = models.FloatField(
        default=1,
        blank=False,
        help_text="Weight of the comparison",
    )

    class Meta:
        unique_together = ["comparison", "criteria"]

    def __str__(self):
        return f"{self.comparison}/{self.criteria}/{self.score}"
