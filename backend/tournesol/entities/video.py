from django.db.models import Q

from .base import EntityType

TYPE_VIDEO = "video"


class VideoEntity(EntityType):
    name = TYPE_VIDEO

    @classmethod
    def filter_date_lte(cls, qs, dt):
        return qs.filter(publication_date__lte=dt)

    @classmethod
    def filter_date_gte(cls, qs, dt):
        return qs.filter(publication_date__gte=dt)

    @classmethod
    def filter_search(cls, qs, query):
        from tournesol.models import Entity

        # Filtering in a nested queryset is necessary here, to be able to annotate
        # each entity without duplicated scores, due to the m2m field 'tags'.
        return qs.filter(pk__in=Entity.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query)
        ))
