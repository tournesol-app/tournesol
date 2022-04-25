"""
Models related to scaling values, used to calibrate individual scores in order
to aggregate them in a Byzantine-resilient manner.
"""

from django.db import models

from core.models import User

from .poll import Poll


class ContributorScaling(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="scalings",
    )
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name="contributor_scalings"
    )
    criteria = models.TextField(
        max_length=32,
        db_index=True,
        help_text="Name of the criteria"
    )
    scale = models.FloatField(
        default=1,
        help_text="Scaling factor, often denoted 's'"
    )
    scale_uncertainty = models.FloatField(
        default=None,
        null=True,
        blank=True,
        help_text="Scaling factor uncertainty"
    )
    translation = models.FloatField(
        default=0,
        help_text="Scaling translation, often denoted 'tau'"
    )
    translation_uncertainty = models.FloatField(
        default=None,
        null=True,
        blank=True,
        help_text="Translation uncertainty",
    )

    class Meta:
        unique_together = ["poll", "criteria", "user"]

    def __str__(self):
        return f"Scaling for {self.poll.name}, {self.criteria}, {self.user}"
