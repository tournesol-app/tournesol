from xml.dom.minidom import Attr
from django.db.models import Q

from .base import EntityType
from tournesol.serializers.metadata import VideoMetadata

TYPE_VIDEO = "video"


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

    @property
    def youtube_video_id(self):
        if self.validated_metadata["source"] == "youtube":
            return self.validated_metadata["video_id"]
        raise AttributeError(f"Entity {self.instance.uid} is not a Youtube video")
