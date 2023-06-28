from django.urls import path

from backoffice.views import BannerListView, TalkEntryListView

urlpatterns = [
    path(
        "talks/",
        TalkEntryListView.as_view(),
        name="talk_list",
    ),
    path(
        "banner/",
        BannerListView.as_view(),
        name="banner_list",
    )
]
