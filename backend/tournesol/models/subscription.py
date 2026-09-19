"""
Subscription model.

A subscription links a user to an `EntitySource` they want to follow.
"""

from django.db import models

from core.models import User
from tournesol.models.entity_source import EntitySource


class Subscription(models.Model):
    """A user's subscription to an `EntitySource`."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        help_text="The user who subscribes to the source.",
    )
    entity_source = models.ForeignKey(
        to=EntitySource,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        help_text="The source the user subscribes to.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user", "-created_at"]
        unique_together = ["user", "entity_source"]

    def __str__(self):
        return f"user:{self.user}/source:{self.entity_source}@{self.created_at}"
