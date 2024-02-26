from django.urls import path

from backoffice.views import (
    BannerListView,
    FAQEntryLocalizedListView,
    OnlineEventListView,
    TalkEntryListView,
)

urlpatterns = [
    path(
        "banners/",
        BannerListView.as_view(),
        name="banner_list",
    ),
    path(
        "events/",
        OnlineEventListView.as_view(),
        name="online_event_list",
    ),
    path(
        "faq/",
        FAQEntryLocalizedListView.as_view(),
        name="faq_list_localized",
    ),
    # Kept for retro-compatibility, use OnlineEventListView instead.
    path(
        "talks/",
        TalkEntryListView.as_view(),
        name="talk_list",
    ),
]
