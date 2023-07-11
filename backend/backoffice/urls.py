from django.urls import path

from backoffice.views import BannerListView, FAQEntryLocalizedListView, TalkEntryListView

urlpatterns = [
    path(
        "faq/",
        FAQEntryLocalizedListView.as_view(),
        name="faq_list_localized",
    ),
    path(
        "talks/",
        TalkEntryListView.as_view(),
        name="talk_list",
    ),
    path(
        "banners/",
        BannerListView.as_view(),
        name="banner_list",
    ),
]
