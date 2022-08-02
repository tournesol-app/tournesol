"""
RateLater model.
"""

from django.db import models

from core.models import User
from tournesol.models.poll import Poll


class RateLater(models.Model):
    """An `Entity` a user wants to rate later in a poll."""

    entity = models.ForeignKey(
        to="Entity",
        on_delete=models.CASCADE,
        help_text="The entity the user wants to save.",
        related_name="ratelaters",
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="The user who saves the entity.",
        related_name="ratelaters",
    )
    poll = models.ForeignKey(
        to=Poll,
        on_delete=models.CASCADE,
        help_text="The poll in which the user is saving the entity.",
        related_name="ratelaters",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Time at which the video is saved.",
        blank=True,
    )

    class Meta:
        ordering = ["user", "-created_at"]
        unique_together = ["poll", "user", "entity"]

    def __str__(self):
        return (
            f"poll:{self.poll}/user:{self.user}/entity:{self.entity}@{self.created_at}"
        )
