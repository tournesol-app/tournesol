from datetime import timedelta
from typing import List

from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.db.models.fields.json import KeyTextTransform
from django.utils import timezone

from tournesol.serializers.metadata import VideoMetadata
from tournesol.utils.constants import YOUTUBE_VIDEO_ID_REGEX

from .base import UID_DELIMITER, EntityType

TYPE_VIDEO = "video"

YOUTUBE_PUBLISHED_AT_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
YOUTUBE_UID_NAMESPACE = "yt"
YOUTUBE_UID_REGEX = (
    rf"({YOUTUBE_UID_NAMESPACE})({UID_DELIMITER})({YOUTUBE_VIDEO_ID_REGEX})"
)


class VideoEntity(EntityType):
    """
    Video entity type

    Handles the metadata specific to videos, retrieved from the YouTube API.
    """

    name = TYPE_VIDEO
    metadata_serializer_class = VideoMetadata

    @classmethod
    def get_allowed_meta_order_fields(cls) -> List[str]:
        """
        Return a list of metadata fields that can be used to order an entity
        list.
        """
        return ["duration", "publication_date"]

    @classmethod
    def get_filter_date_field(cls):
        return "metadata__publication_date"

    @classmethod
    def filter_date_lte(cls, qs, max_date):
        return qs.filter(metadata__publication_date__lte=max_date.isoformat())

    @classmethod
    def filter_date_gte(cls, qs, min_date):
        return qs.filter(metadata__publication_date__gte=min_date.isoformat())

    @classmethod
    def get_uid_regex(cls, namespace: str) -> str:
        if namespace == YOUTUBE_UID_NAMESPACE:
            return YOUTUBE_UID_REGEX
        return ""

    def update_metadata_field(self, compute_language=False, **kwargs) -> None:
        # pylint: disable=import-outside-toplevel
        from tournesol.utils.api_youtube import VideoNotFound, get_video_metadata

        try:
            metadata = get_video_metadata(
                self.instance.metadata["video_id"], compute_language=compute_language
            )
        except VideoNotFound:
            metadata = {}

        if not metadata:
            return

        for (metadata_key, metadata_value) in metadata.items():
            if metadata_value is not None:
                self.instance.metadata[metadata_key] = metadata_value

    def metadata_needs_to_be_refreshed(self) -> bool:
        """
        Refresh will be executed only if the current metadata
        are too old, relatively to the video publication date.
        The request can be forced with `.refresh_metadata(force=True)`.
        """
        if self.instance.last_metadata_request_at is None:
            return True

        now = timezone.now()
        since_last_request = now - self.instance.last_metadata_request_at
        if since_last_request < timedelta(minutes=1):
            return False
        if since_last_request > timedelta(days=30):
            return True

        publication_date = self.validated_metadata["publication_date"]
        if publication_date is None:
            return False

        since_publication = now - publication_date
        ratio = since_last_request / since_publication
        return ratio > settings.VIDEO_METADATA_REFRESH_THRESHOLD

    @classmethod
    def update_search_vector(cls, entity) -> None:
        # pylint: disable=import-outside-toplevel
        from tournesol.utils.video_language import language_to_postgres_config

        language_config = language_to_postgres_config(entity.metadata["language"])

        entity.search_config_name = language_config
        entity.search_vector = (
            SearchVector("uid", weight="A", config=language_config)
            + SearchVector(
                KeyTextTransform("name", "metadata"), weight="A", config=language_config
            )
            + SearchVector(
                KeyTextTransform("uploader", "metadata"),
                weight="A",
                config=language_config,
            )
            + SearchVector(
                KeyTextTransform("tags", "metadata"), weight="A", config=language_config
            )
            + SearchVector(
                KeyTextTransform("description", "metadata"),
                weight="C",
                config=language_config,
            )
        )

        entity.save(update_fields=["search_config_name", "search_vector"])
