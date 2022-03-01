from django.db.models import Q

from core.utils.constants import YOUTUBE_VIDEO_ID_REGEX
from tournesol.serializers.metadata import VideoMetadata

from .base import EntityType

TYPE_VIDEO = "video"

YOUTUBE_UID_NAMESPACE = 'yt'
YOUTUBE_UID_REGEX = rf"{YOUTUBE_UID_NAMESPACE}:{YOUTUBE_VIDEO_ID_REGEX[1:]}"


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
    def filter_search(cls, qs, query):
        from tournesol.models import Entity
        return qs.filter(pk__in=Entity.objects.filter(
            Q(metadata__name__icontains=query) |
            Q(metadata__description__icontains=query) |
            Q(metadata__tags__icontains=query)
        ))

    @classmethod
    def get_uid_regex(cls, namespace):
        if namespace == YOUTUBE_UID_NAMESPACE:
            return YOUTUBE_UID_REGEX
        return None
