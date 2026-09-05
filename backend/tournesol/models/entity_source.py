"""
EntitySource model.

A source produces entities. A YouTube channel, for example, is the source of
the videos it publishes. Users subscribe to sources to build a personalized
feed of the entities these sources produce.
"""

from django.db import models

from tournesol.entities.base import UID_DELIMITER
from tournesol.entities.video import YOUTUBE_UID_NAMESPACE
from tournesol.utils.constants import YOUTUBE_CHANNEL_ID_REGEX

# The pattern a whole source uid must match, per uid namespace.
UID_REGEX_BY_NAMESPACE = {
    YOUTUBE_UID_NAMESPACE: rf"{YOUTUBE_UID_NAMESPACE}{UID_DELIMITER}{YOUTUBE_CHANNEL_ID_REGEX}",
}


class EntitySource(models.Model):
    """A source that produces entities, such as a YouTube channel."""

    uid = models.CharField(
        unique=True,
        max_length=144,
        help_text="A unique identifier, built with a namespace and an external id.",
    )
    metadata = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.uid

    @classmethod
    def get_or_create_from_uid(cls, uid: str) -> "EntitySource":
        source, _created = cls.objects.get_or_create(uid=uid)
        return source
