# coding: utf-8

"""
Defines Tournesol's backend API routes
"""

from django.urls import include, path
from rest_framework import routers

from .views import ComparisonDetailApi, ComparisonListApi, ComparisonListFilteredApi
from .views.email_domains import EmailDomainsList
from .views.entities import EntitiesViewSet
from .views.exports import ExportAllView, ExportComparisonsView, ExportPublicComparisonsView
from .views.polls import PollsRecommendationsView, PollsView
from .views.ratings import (
    ContributorRatingDetail,
    ContributorRatingList,
    ContributorRatingUpdateAll,
)
from .views.stats import StatisticsView
from .views.user import CurrentUserView
from .views.video import VideoViewSet
from .views.video_rate_later import VideoRateLaterDetail, VideoRateLaterList

router = routers.DefaultRouter()
router.register(r'video', VideoViewSet, basename="video")
router.register(r'entities', EntitiesViewSet)

app_name = "tournesol"
urlpatterns = [
    path("", include(router.urls)),
    # User API
    path(
        "users/me/",
        CurrentUserView.as_view(),
        name="users_me"
    ),
    # Data exports
    path(
        "users/me/exports/comparisons/",
        ExportComparisonsView.as_view(),
        name="export_comparisons"
    ),
    path(
        "users/me/exports/all/",
        ExportAllView.as_view(),
        name="export_all"
    ),
    path(
        "exports/comparisons/",
        ExportPublicComparisonsView.as_view(),
        name="export_public"
    ),
    # Comparison API
    path(
        "users/me/comparisons/<str:poll_name>", ComparisonListApi.as_view(),
        name="poll_comparisons_me_list",
    ),
    path(
        "users/me/comparisons/<str:poll_name>/<str:uid>/",
        ComparisonListFilteredApi.as_view(),
        name="poll_comparisons_me_list_filtered",
    ),
    path(
        "users/me/comparisons/<str:poll_name>/<str:uid_a>/<str:uid_b>/",
        ComparisonDetailApi.as_view(),
        name="poll_comparisons_me_detail",
    ),
    # VideoRateLater API
    path(
        "users/me/video_rate_later/",
        VideoRateLaterList.as_view(),
        name="video_rate_later_list",
    ),
    path(
        "users/me/video_rate_later/<str:video_id>/",
        VideoRateLaterDetail.as_view(),
        name="video_rate_later_detail",
    ),
    # Ratings API
    path(
        "users/me/contributor_ratings/",
        ContributorRatingList.as_view(),
        name="ratings_me_list",
    ),
    path(
        "users/me/contributor_ratings/_all/",
        ContributorRatingUpdateAll.as_view(),
        name="ratings_me_list_update_is_public",
    ),
    path(
        "users/me/contributor_ratings/<str:video_id>/",
        ContributorRatingDetail.as_view(),
        name="ratings_me_detail",
    ),
    # Email domain API
    path(
        "domains/",
        EmailDomainsList.as_view(),
        name="email_domains_list"
    ),
    # Statistics API
    path(
        "stats/",
        StatisticsView.as_view(),
        name="statistics_detail"
    ),
    # Polls API
    path(
        "polls/<str:name>/",
        PollsView.as_view(),
        name="polls_detail"
    ),
    path(
        "polls/<str:name>/recommendations/",
        PollsRecommendationsView.as_view(),
        name="polls_recommendations"
    ),
]
