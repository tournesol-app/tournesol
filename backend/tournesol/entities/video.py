from datetime import timedelta

from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.utils import timezone

from tournesol.serializers.metadata import VideoMetadata
from tournesol.utils.constants import YOUTUBE_VIDEO_ID_REGEX

from .base import UID_DELIMITER, EntityType

TYPE_VIDEO = "video"

YOUTUBE_UID_NAMESPACE = "yt"
YOUTUBE_UID_REGEX = (
    rf"({YOUTUBE_UID_NAMESPACE})({UID_DELIMITER})({YOUTUBE_VIDEO_ID_REGEX})"
)


class VideoEntity(EntityType):
    name = TYPE_VIDEO
    metadata_serializer_class = VideoMetadata

    @classmethod
    def filter_date_lte(cls, qs, dt):
        return qs.filter(metadata__publication_date__lte=dt.date().isoformat())

    @classmethod
    def filter_date_gte(cls, qs, dt):
        return qs.filter(metadata__publication_date__gte=dt.date().isoformat())

    @classmethod
    def get_uid_regex(cls, namespace: str) -> str:
        if namespace == YOUTUBE_UID_NAMESPACE:
            return YOUTUBE_UID_REGEX
        return ''

    def update_metadata_field(self) -> None:
        from tournesol.utils.api_youtube import VideoNotFound, get_video_metadata
        try:
            metadata = get_video_metadata(
                self.instance.metadata["video_id"], compute_language=False
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
        are older than `VIDEO_METADATA_EXPIRE_SECONDS`.
        The request can be forced with `.refresh_metadata(force=True)`.
        """
        return self.instance.last_metadata_request_at is None or (
            timezone.now() - self.instance.last_metadata_request_at
            >= timedelta(seconds=settings.VIDEO_METADATA_EXPIRE_SECONDS)
        )

    @classmethod
    def update_search_vector(cls, entity) -> None:
        from tournesol.utils.video_language import language_to_postgres_config

        language_config = language_to_postgres_config(entity.metadata["language"])

        entity.search_config_name = language_config
        entity.search_vector = \
            SearchVector("uid", weight="A", config=language_config) + \
            SearchVector("metadata__name", weight="A", config=language_config) + \
            SearchVector("metadata__uploader", weight="A", config=language_config) + \
            SearchVector("metadata__tags", weight="A", config=language_config) + \
            SearchVector("metadata__description", weight="C", config=language_config)

        entity.save(update_fields=["search_config_name", "search_vector"])
