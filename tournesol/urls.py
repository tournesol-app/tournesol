# coding: utf-8

"""
Defines Tournesol's backend API routes
"""

from django.urls import include, path
from rest_framework import routers

from .views import ComparisonDetailApi, ComparisonListApi, ComparisonListOnlyApi
from .views.video import VideoViewSet
from .views.video_rate_later import VideoRateLaterDetail, VideoRateLaterList


router = routers.DefaultRouter()
router.register(r'video', VideoViewSet)

app_name = "tournesol"
urlpatterns = [
    path("", include(router.urls)),
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
        "users/<str:username>/video_rate_later/",
        VideoRateLaterList.as_view(),
        name="video_rate_later_list",
    ),
    path(
        "users/<str:username>/video_rate_later/<str:video_id>/",
        VideoRateLaterDetail.as_view(),
        name="video_rate_later_detail",
    )
]
