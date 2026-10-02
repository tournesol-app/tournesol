"""
EntitySource model.

A source produces entities. A YouTube channel, for example, is the source of
the videos it publishes. Users subscribe to sources to build a personalized
feed of the entities these sources produce.
"""

import logging
from datetime import timedelta

from django.db import models
from django.utils import timezone

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
    metadata_timestamp = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp the metadata was updated",
    )
    last_metadata_request_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time fetch of metadata was attempted",
    )
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

    def metadata_needs_to_be_refreshed(self) -> bool:
        if self.last_metadata_request_at is None:
            return True

        now = timezone.now()
        since_last_request = now - self.last_metadata_request_at
        if since_last_request > timedelta(days=30):
            return True

        return False

    def update_metadata_field(self) -> None:
        try:
            metadata = EntitySource.fetch_metadata(self.uid)
        except SourceNotFound:
            metadata = {}

        if not metadata:
            return

        for (metadata_key, metadata_value) in metadata.items():
            if metadata_value is not None:
                self.metadata[metadata_key] = metadata_value

    def refresh_metadata(self, force=False, save=True) -> None:
        if not force and not self.metadata_needs_to_be_refreshed():
            logging.debug(
                "Not refreshing metadata for entity source %s. Last attempt at %s",
                self.uid,
                self.last_metadata_request_at,
            )
            return

        self.last_metadata_request_at = timezone.now()
        if save:
            # Let's update 'last_metadata_request_at' as soon as possible,
            # to avoid repeated metadata refreshes, due to concurrent requests
            # or unexpected errors in the refresh process.
            self.save(update_fields=["last_metadata_request_at"])

        self.update_metadata_field()
        # TODO: implement cleaned_metadata
        # Ensure that the metadata format is valid after refresh
        # self.instance.metadata = self.cleaned_metadata
        self.metadata_timestamp = timezone.now()
        if save:
            self.save(update_fields=["metadata", "metadata_timestamp"])
