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


class SourceNotFound(Exception):
    """The source does not exist on its platform."""


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
        existing_source = cls.objects.filter(uid=uid).first()
        if existing_source is not None:
            return existing_source

        metadata = cls.fetch_metadata(uid)
        source, _created = cls.objects.get_or_create(
            uid=uid, defaults={"metadata": metadata}
        )
        return source

    @staticmethod
    def fetch_metadata(uid: str) -> dict:
        """
        Fetch the metadata of a source from its platform.

        Only YouTube channels are supported for now; the namespace is validated
        upstream, before this is reached. Raise `SourceNotFound` if the source
        does not exist on its platform.
        """
        # pylint: disable=import-outside-toplevel
        from tournesol.utils.api_youtube import ChannelNotFound, get_channel_metadata

        channel_id = uid.split(UID_DELIMITER, maxsplit=1)[1]
        try:
            return get_channel_metadata(channel_id)
        except ChannelNotFound as error:
            raise SourceNotFound(uid) from error
