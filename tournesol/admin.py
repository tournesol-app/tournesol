from tournesol.models.video import ComparisonCriteriaScore
from django.contrib import admin

from .models import (
    Video, VideoCriteriaScore, 
    ContributorRating, ContributorRatingCriteriaScore, 
    Comparison, ComparisonCriteriaScore)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    pass


@admin.register(VideoCriteriaScore)
class VideoCriteriaScoreAdmin(admin.ModelAdmin):
    pass


@admin.register(ContributorRating)
class ContributorRatingAdmin(admin.ModelAdmin):
    pass


@admin.register(ContributorRatingCriteriaScore)
class ContributorRatingCriteriaScoreAdmin(admin.ModelAdmin):
    pass


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    pass


@admin.register(ComparisonCriteriaScore)
class ComparisonCriteriaScoreAdmin(admin.ModelAdmin):
    pass