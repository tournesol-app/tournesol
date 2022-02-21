"""
Defines Tournesol's backend admin interface
"""

from django.contrib import admin

from tournesol.entities.video import TYPE_VIDEO

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


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = (
        'uid',
        'name',
        'uploader',
        'publication_date',
        'rating_n_ratings',
        'rating_n_contributors',
        'language',
        'link_to_youtube',
    )
    search_fields = ('uid', 'name', 'uploader')
    list_filter = (
        'type',
        ('language', admin.AllValuesFieldListFilter),
    )
    actions = ["update_metadata"]

    @admin.action(description="Force metadata refresh of selected videos")
    def update_metadata(self, request, queryset):
        for entity in queryset.iterator():
            if entity.type == TYPE_VIDEO:
                entity.refresh_youtube_metadata(force=True)


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
