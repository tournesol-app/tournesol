"""
Defines Tournesol's backend admin interface
"""

from django.contrib import admin

from .models import (
    Video,
    VideoCriteriaScore,
    ContributorRating,
    ContributorRatingCriteriaScore,
    Comparison,
    ComparisonCriteriaScore,
)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        'video_id',
        'name',
        'uploader',
        'publication_date',
        'rating_n_ratings',
        'rating_n_contributors',
        'language',
        'link_to_youtube',
    )
    search_fields = ('video_id', 'name', 'uploader')
    list_filter = (
        ('language', admin.AllValuesFieldListFilter),
    )
    actions = ["update_metadata"]

    @admin.action(description="Force metadata refresh of selected videos")
    def update_metadata(self, request, queryset):
        for video in queryset:
            video.refresh_youtube_metadata(force=True)


@admin.register(VideoCriteriaScore)
class VideoCriteriaScoreAdmin(admin.ModelAdmin):
    pass


@admin.register(ContributorRating)
class ContributorRatingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'video',
        'link_to_youtube',
        'is_public',
    )
    list_filter = (
        'is_public',
    )

    def link_to_youtube(self, obj):
        return obj.video.link_to_youtube()


@admin.register(ContributorRatingCriteriaScore)
class ContributorRatingCriteriaScoreAdmin(admin.ModelAdmin):
    pass


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    pass


@admin.register(ComparisonCriteriaScore)
class ComparisonCriteriaScoreAdmin(admin.ModelAdmin):
    pass
