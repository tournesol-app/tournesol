"""
Rate later element related.
"""

from django.db import models
from .poll import Poll

from core.models import User


class RateLater(models.Model):
    """List of videos that a person wants to rate later."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="Person who saves the video",
        related_name="ratelaters",
    )
    poll = models.ForeignKey(
        to=Poll,
        on_delete=models.CASCADE,
        help_text="Poll associated with the entity to rate later",
        related_name="ratelaters",
        blank=True,
        default=Poll.default_poll_pk,
    )
    entity = models.ForeignKey(
        to="Entity",
        on_delete=models.CASCADE,
        help_text="Entity in the rate later list",
        related_name="ratelaters",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the video was added to the" " rate later list",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ["poll", "user", "entity"]
        ordering = ["user", "-created_at"]

    def __str__(self):
        return f"poll:{self.poll}/user:{self.user}/entity:{self.video}@{self.created_at}"
