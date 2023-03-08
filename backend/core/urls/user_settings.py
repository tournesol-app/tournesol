"""
The `core` app routes related to user settings.
"""

from django.urls import path

from core.views.user_settings import UserSettingsDetail

urlpatterns = [
    path(
        "settings/",
        UserSettingsDetail.as_view(),
        name="usersettings_detail",
    ),
]
