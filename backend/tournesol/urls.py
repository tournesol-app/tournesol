# coding: utf-8

"""
Defines Tournesol's backend API routes
"""

from django.urls import path

from .views import ComparisonDetailApi, ComparisonListApi, ComparisonListOnlyApi
from .views.exports import ExportComparisonsView, ExportAllView
from .views.video import VideoView, VideoRetrieveView
from .views.video_rate_later import VideoRateLaterDetail, VideoRateLaterList
from .views.user import CurrentUserView
from .views.ratings import ContributorRatingList, ContributorRatingDetail
from .views.email_domains import EmailDomainsList


app_name = "tournesol"
urlpatterns = [
    # Video API
    # TODO: the endpoint below is duplicated for backward compatinility.
    # We want to keep the enpoints `videos/` and `videos/{id}`
    path(
        "video/",
        VideoView.as_view(),
        name="list_video"
    ),
    path(
        "video/<str:youtube_id>/",
        VideoRetrieveView.as_view(),
        name="retrieve_video"
    ),
    path(
        "videos/",
        VideoView.as_view(),
        name="list_videos"
    ),
    path(
        "videos/<str:youtube_id>/",
        VideoRetrieveView.as_view(),
        name="retrieve_videos"
    ),
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
    path(
        "domains/",
        EmailDomainsList.as_view(),
        name="email_domains_list"
    )
]
