"""
Rate later element related.
"""

from django.db import models

from core.models import User


class RateLater(models.Model):
    """List of videos that a person wants to rate later."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="Person who saves the video",
        related_name="ratelaters",
    )
    video = models.ForeignKey(
        to="Entity",
        on_delete=models.CASCADE,
        help_text="Video in the rate later list",
        related_name="ratelaters",
    )

    datetime_add = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the video was added to the" " rate later list",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ["user", "video"]
        ordering = ["user", "-datetime_add"]

    def __str__(self):
        return f"{self.user}/{self.video}@{self.datetime_add}"
