from django.urls import path

from backoffice.views import BannerListView, FAQEntryLocalizedListView, TournesolEventListView

urlpatterns = [
    path(
        "banners/",
        BannerListView.as_view(),
        name="banner_list",
    ),
    path(
        "events/",
        TournesolEventListView.as_view(),
        name="tournesol_event_list",
    ),
    path(
        "faq/",
        FAQEntryLocalizedListView.as_view(),
        name="faq_list_localized",
    ),
]
