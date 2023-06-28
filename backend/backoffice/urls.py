from django.urls import path

from backoffice.views import TalkEntryListView

urlpatterns = [
    path(
        "talks/",
        TalkEntryListView.as_view(),
        name="talk_list",
    ),
]
