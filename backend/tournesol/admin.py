"""
Defines Tournesol's backend admin interface
"""

from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.db.models import Q

from .entities.video import TYPE_VIDEO
from .models import (
    Comparison,
    ComparisonCriteriaScore,
    ContributorRating,
    ContributorRatingCriteriaScore,
    Criteria,
    CriteriaLocale,
    CriteriaRank,
    Entity,
    EntityCriteriaScore,
    Poll,
)
from .utils.video_language import LANGUAGE_CODE_TO_NAME_MATCHING


class MetadataFieldFilter(SimpleListFilter):
    parameter_name = None
    metadata_key = None

    def lookups(self, request, model_admin):
        field_values = sorted(
            model_admin.model.objects
            .distinct()
            .exclude(**{f"metadata__{self.metadata_key}": None})
            .values_list(f"metadata__{self.metadata_key}", flat=True)
        )
        return [("", "-")] + [(v, v) for v in field_values]

    def queryset(self, request, queryset):
        if self.value():
            json_field_query = {f"metadata__{self.metadata_key}": self.value()}
            return queryset.filter(**json_field_query)
        elif self.value() == "":
            json_field_query = (
                Q(**{f"metadata__{self.metadata_key}": ""})
                | Q(**{f"metadata__{self.metadata_key}": None})
            )
            return queryset.filter(json_field_query)
        else:
            return queryset


class EntityLanguageFilter(MetadataFieldFilter):
    title = "language"
    parameter_name = "metadataLanguage"
    metadata_key = "language"


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = (
        'uid',
        'get_name',
        'get_uploader',
        'get_publication_date',
        'rating_n_ratings',
        'rating_n_contributors',
        'get_language',
        'link_to_youtube',
    )
    search_fields = ('uid', 'metadata__name', 'metadata__uploader')
    list_filter = (
        'type',
        EntityLanguageFilter,
    )
    actions = ["update_metadata"]

    @admin.action(description="Force metadata refresh of selected videos")
    def update_metadata(self, request, queryset):
        for entity in queryset.iterator():
            if entity.type == TYPE_VIDEO:
                entity.refresh_youtube_metadata(force=True)

    @staticmethod
    @admin.display(description="name", ordering="metadata__name")
    def get_name(obj):
        return obj.metadata.get("name")

    @staticmethod
    @admin.display(description="uploader", ordering="metadata__uploader")
    def get_uploader(obj):
        return obj.metadata.get("uploader")

    @staticmethod
    @admin.display(description="publication_date", ordering="metadata__publication_date")
    def get_publication_date(obj):
        return obj.metadata.get("publication_date")

    @staticmethod
    @admin.display(description="language", ordering="metadata__language")
    def get_language(obj):
        language_code = obj.metadata.get("language")
        return LANGUAGE_CODE_TO_NAME_MATCHING.get(language_code, language_code)


@admin.register(EntityCriteriaScore)
class EntityCriteriaScoreAdmin(admin.ModelAdmin):
    pass


@admin.register(ContributorRating)
class ContributorRatingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'entity',
        'get_poll_name',
        'link_to_youtube',
        'is_public',
    )
    list_filter = (
        'poll__name',
        'entity__type',
        'is_public',
    )
    list_select_related = (
        'poll',
        'entity',
    )

    def link_to_youtube(self, obj):
        return obj.entity.link_to_youtube()

    @admin.display(ordering="poll__name", description="Poll")
    def get_poll_name(self, obj):
        return obj.poll.name


@admin.register(ContributorRatingCriteriaScore)
class ContributorRatingCriteriaScoreAdmin(admin.ModelAdmin):
    pass


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'get_poll_name',
        'entity_1',
        'entity_2',
        'datetime_lastedit',
    )
    list_filter = (
        'poll__name',
    )
    list_select_related = (
        'entity_1',
        'entity_2',
        'poll',
    )
    raw_id_fields = (
        'user',
        'entity_1',
        'entity_2',
    )

    @admin.display(ordering="poll__name", description="Poll")
    def get_poll_name(self, obj):
        return obj.poll.name


@admin.register(ComparisonCriteriaScore)
class ComparisonCriteriaScoreAdmin(admin.ModelAdmin):
    pass


class CriteriasInline(admin.TabularInline):
    model = CriteriaRank
    extra = 0


class CriteriaLocalesInline(admin.TabularInline):
    model = CriteriaLocale
    extra = 0


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'entity_type',
        'get_n_criterias',
    )
    inlines = (CriteriasInline,)

    @admin.display(description="Nb of criterias")
    def get_n_criterias(self, obj):
        return obj.criterias.count()


@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    inlines = (
        CriteriaLocalesInline,
    )
