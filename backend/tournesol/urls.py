# coding: utf-8

"""
Defines Tournesol's backend API routes
"""

from django.urls import include, path
from rest_framework import routers

from .views import ComparisonDetailApi, ComparisonListApi, ComparisonListOnlyApi
from .views.video import VideoViewSet
from .views.video_rate_later import VideoRateLaterDetail, VideoRateLaterList
from .views.user import CurrentUserView
from .views.ratings import ContributorRatingList, ContributorRatingDetail


router = routers.DefaultRouter()
router.register(r'video', VideoViewSet)

app_name = "tournesol"
urlpatterns = [
    path("", include(router.urls)),
    # User API
    path(
        "users/me/",
        CurrentUserView.as_view(),
        name="users_me"
    ),
    # Comparison API
    path(
        "users/me/comparisons/", ComparisonListApi.as_view(),
        name="comparisons_me_list",
    ),
    path(
        "users/me/comparisons/<str:video_id>/", ComparisonListOnlyApi.as_view(),
        name="comparisons_me_list_filtered",
    ),
    path(
        "users/me/comparisons/<str:video_id_a>/<str:video_id_b>/",
        ComparisonDetailApi.as_view(),
        name="comparisons_me_detail",
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
        "users/me/contributor_ratings/<str:video_id>/",
        ContributorRatingDetail.as_view(),
        name="ratings_me_detail",
    ),
]
