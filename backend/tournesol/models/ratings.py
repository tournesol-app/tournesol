"""
Models for Tournesol's main functions related to contributor's ratings
"""

from django.db import models

from core.models import User

from .entity import Entity
from .poll import Poll


class ContributorRating(models.Model):
    """Predictions by individual contributor models."""

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        help_text="Entity being scored",
        related_name="contributorvideoratings",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The contributor",
        related_name="contributorvideoratings",
    )
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name="contributor_ratings",
        default=Poll.default_poll_pk
    )
    is_public = models.BooleanField(
        default=False, null=False, help_text="Should the rating be public?"
    )

    class Meta:
        unique_together = ["user", "entity", "poll"]

    def __str__(self):
        return "%s on %s" % (self.user, self.entity)


class ContributorRatingCriteriaScore(models.Model):
    """Scores per criteria for contributors' algorithmic representatives"""

    contributor_rating = models.ForeignKey(
        to=ContributorRating,
        help_text="Foreign key to the contributor's rating",
        related_name="criteria_scores",
        on_delete=models.CASCADE,
    )
    criteria = models.TextField(
        max_length=32,
        help_text="Name of the criteria",
        db_index=True,
    )
    score = models.FloatField(
        default=0,
        blank=False,
        help_text="Score for the given criteria",
    )
    uncertainty = models.FloatField(
        default=0,
        blank=False,
        help_text="Uncertainty about the video's score for the given criteria",
    )

    class Meta:
        unique_together = ["contributor_rating", "criteria"]

    def __str__(self):
        return f"{self.contributor_rating}/{self.criteria}/{self.score}"
